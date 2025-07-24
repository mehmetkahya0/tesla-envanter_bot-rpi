import os
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TeslaInventoryBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))
        self.models = json.loads(os.getenv('MODELS', '["Model 3", "Model Y"]'))
        self.tesla_url = os.getenv('TESLA_URL', 'https://www.tesla.com/tr_tr/inventory/new')
        self.data_dir = os.getenv('DATA_DIR', '/app/data')
        
        self.bot = Bot(token=self.telegram_token)
        self.last_vehicles = set()
        self.data_file = os.path.join(self.data_dir, 'last_inventory.json')
        self.is_monitoring = True
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load last known inventory
        self.load_last_inventory()
        
        logger.info(f"Bot initialized. Monitoring models: {self.models}")
    
    def load_last_inventory(self):
        """Load last known inventory from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_vehicles = set(data.get('vehicles', []))
                logger.info(f"Loaded {len(self.last_vehicles)} vehicles from cache")
        except Exception as e:
            logger.error(f"Error loading last inventory: {e}")
            self.last_vehicles = set()
    
    def save_last_inventory(self):
        """Save current inventory to file"""
        try:
            data = {
                'vehicles': list(self.last_vehicles),
                'last_update': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving inventory: {e}")
    
    def get_tesla_inventory(self):
        """Scrape Tesla Turkey inventory"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # Tesla Turkey inventory URL
            url = self.tesla_url
            
            logger.info(f"Fetching Tesla inventory from: {url}")
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            
            if response.status_code == 403:
                logger.warning("403 Forbidden - Tesla may be blocking requests. Trying alternative approach...")
                # Try with different approach or simulate browser
                import time
                time.sleep(2)  # Small delay
                
                # Try again with minimal headers
                simple_headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=simple_headers, timeout=30)
            
            response.raise_for_status()
            logger.info(f"Successfully fetched page, content length: {len(response.content)}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            vehicles = []
            
            # Look for vehicle cards (Tesla's structure may change)
            # Try multiple selectors
            possible_selectors = [
                'div[data-testid*="vehicle"]',
                'article[data-testid*="vehicle"]',
                '.vehicle-card',
                '.inventory-card',
                '[class*="vehicle"]',
                '[class*="inventory"]'
            ]
            
            vehicle_cards = []
            for selector in possible_selectors:
                cards = soup.select(selector)
                if cards:
                    vehicle_cards.extend(cards)
                    logger.debug(f"Found {len(cards)} cards with selector: {selector}")
            
            # If no specific selectors work, try broader approach
            if not vehicle_cards:
                vehicle_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['vehicle', 'car', 'inventory', 'product']
                ))
            
            logger.info(f"Found {len(vehicle_cards)} potential vehicle cards")
            
            for card in vehicle_cards:
                try:
                    # Extract vehicle information
                    text_content = card.get_text(strip=True)
                    
                    # Check if any of our monitored models are mentioned
                    model_found = None
                    for model in self.models:
                        if model.lower() in text_content.lower():
                            model_found = model
                            break
                    
                    if model_found:
                        # Create unique identifier for the vehicle
                        vehicle_id = f"{model_found}_{hash(text_content) % 10000}"
                        
                        vehicle_info = {
                            'id': vehicle_id,
                            'model': model_found,
                            'details': text_content[:200],  # First 200 chars
                            'url': url
                        }
                        
                        vehicles.append(vehicle_info)
                        logger.debug(f"Found vehicle: {model_found}")
                        
                except Exception as e:
                    logger.debug(f"Error parsing vehicle card: {e}")
                    continue
            
            logger.info(f"Found {len(vehicles)} vehicles in inventory")
            
            # If no vehicles found, log page content for debugging (first 500 chars)
            if not vehicles:
                logger.debug(f"No vehicles found. Page content preview: {soup.get_text()[:500]}")
            
            return vehicles
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Tesla inventory: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    async def send_telegram_message(self, message, reply_to_message_id=None):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False,
                reply_to_message_id=reply_to_message_id
            )
            logger.info("Telegram message sent successfully")
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    async def process_command(self, command, message_id=None):
        """Process bot commands"""
        try:
            if command == '/start':
                message = "🤖 <b>Tesla Envanter Bot'a Hoş Geldiniz!</b>\n\n"
                message += "🚗 Bu bot Tesla Türkiye envanterini takip eder ve yeni araçlar geldiğinde bildirim gönderir.\n\n"
                message += "<b>📋 Kullanılabilir Komutlar:</b>\n"
                message += "/help - Bu yardım mesajını gösterir\n"
                message += "/ping - Bot'un çalışıp çalışmadığını kontrol eder\n"
                message += "/manuel-arama - Envanterde manuel arama yapar\n"
                message += "/durum - Bot durumunu ve ayarlarını gösterir\n"
                message += "/durdur - Otomatik takibi durdurur\n"
                message += "/basla - Otomatik takibi başlatır\n"
                message += "/modeller - Takip edilen modelleri gösterir\n\n"
                message += f"📊 <b>Takip Edilen Modeller:</b> {', '.join(self.models)}\n"
                message += f"⏰ <b>Kontrol Aralığı:</b> {self.check_interval} saniye\n"
                message += f"🔄 <b>Otomatik Takip:</b> {'Aktif' if self.is_monitoring else 'Pasif'}"
                
            elif command == '/help':
                message = "🆘 <b>Tesla Envanter Bot Yardım</b>\n\n"
                message += "<b>📋 Komutlar:</b>\n\n"
                message += "🏁 <b>/start</b> - Bot'u başlatır ve ana menüyü gösterir\n"
                message += "📋 <b>/help</b> - Bu yardım mesajını gösterir\n"
                message += "🏓 <b>/ping</b> - Bot'un çalışıp çalışmadığını test eder\n"
                message += "🔍 <b>/manuel-arama</b> - Tesla envanterinde manuel arama yapar\n"
                message += "📊 <b>/durum</b> - Bot durumu ve ayarlarını gösterir\n"
                message += "⏹️ <b>/durdur</b> - Otomatik envanter takibini durdurur\n"
                message += "▶️ <b>/basla</b> - Otomatik envanter takibini başlatır\n"
                message += "🚗 <b>/modeller</b> - Takip edilen araç modellerini gösterir\n\n"
                message += "<b>ℹ️ Nasıl Çalışır?</b>\n"
                message += "• Bot düzenli aralıklarla Tesla Türkiye sitesini kontrol eder\n"
                message += "• Yeni araç geldiğinde otomatik bildirim gönderir\n"
                message += "• Manuel olarak da arama yapabilirsiniz\n\n"
                message += "<b>⚠️ Not:</b> Bot yalnızca belirtilen modelleri takip eder."
                
            elif command == '/ping':
                message = "🏓 <b>Pong!</b>\n\n"
                message += "✅ Bot çalışıyor ve komutlara yanıt veriyor.\n"
                message += f"⏰ Son kontrol: {datetime.now().strftime('%H:%M:%S')}\n"
                message += f"🔄 Otomatik takip: {'Aktif' if self.is_monitoring else 'Pasif'}"
                
            elif command == '/durum':
                message = "📊 <b>Bot Durumu</b>\n\n"
                message += f"🔄 <b>Otomatik Takip:</b> {'🟢 Aktif' if self.is_monitoring else '🔴 Pasif'}\n"
                message += f"🚗 <b>Takip Edilen Modeller:</b> {', '.join(self.models)}\n"
                message += f"⏰ <b>Kontrol Aralığı:</b> {self.check_interval} saniye\n"
                message += f"📁 <b>Kayıtlı Araç Sayısı:</b> {len(self.last_vehicles)}\n"
                message += f"🌐 <b>Tesla URL:</b> {self.tesla_url}\n"
                message += f"🕐 <b>Son Güncelleme:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                
            elif command == '/modeller':
                message = "🚗 <b>Takip Edilen Tesla Modelleri</b>\n\n"
                for i, model in enumerate(self.models, 1):
                    message += f"{i}. {model}\n"
                
                message += f"\n📊 <b>Toplam:</b> {len(self.models)} model\n"
                message += "\n💡 <b>Not:</b> Model listesini değiştirmek için bot ayarlarını güncelleyin."
                
            elif command == '/durdur':
                self.is_monitoring = False
                message = "⏹️ <b>Otomatik takip durduruldu</b>\n\n"
                message += "🔴 Artık otomatik envanter kontrolü yapılmayacak.\n"
                message += "▶️ Tekrar başlatmak için <b>/basla</b> komutunu kullanın.\n"
                message += "🔍 Manuel arama için <b>/manuel-arama</b> komutunu kullanabilirsiniz."
                logger.info("Monitoring stopped by user command")
                
            elif command == '/basla':
                self.is_monitoring = True
                message = "▶️ <b>Otomatik takip başlatıldı</b>\n\n"
                message += "🟢 Otomatik envanter kontrolü aktif.\n"
                message += f"⏰ Her {self.check_interval} saniyede bir kontrol edilecek.\n"
                message += "⏹️ Durdurmak için <b>/durdur</b> komutunu kullanın."
                logger.info("Monitoring started by user command")
                
            elif command == '/manuel-arama':
                await self.send_telegram_message(
                    "🔍 <b>Manuel arama başlatılıyor...</b>\n\nTesla envanteri kontrol ediliyor, lütfen bekleyin...",
                    reply_to_message_id=message_id
                )
                
                try:
                    vehicles = self.get_tesla_inventory()
                    
                    if vehicles:
                        message = f"🎉 <b>Envanterde {len(vehicles)} araç bulundu!</b>\n\n"
                        for vehicle in vehicles[:5]:  # İlk 5 aracı göster
                            message += f"🚗 <b>{vehicle['model']}</b>\n"
                            message += f"📝 {vehicle['details'][:100]}...\n\n"
                        
                        if len(vehicles) > 5:
                            message += f"... ve {len(vehicles) - 5} araç daha\n\n"
                        
                        message += f"🔗 <a href='{self.tesla_url}'>Tüm Envanteri Görüntüle</a>"
                    else:
                        message = "😔 <b>Envanterde araç bulunamadı</b>\n\n"
                        message += "Takip edilen modellerde şu anda uygun araç yok.\n"
                        message += f"🚗 Aranan modeller: {', '.join(self.models)}\n\n"
                        message += f"🔗 <a href='{self.tesla_url}'>Tesla Sitesini Kontrol Et</a>"
                    
                except Exception as e:
                    message = "❌ <b>Manuel arama hatası</b>\n\n"
                    message += "Envanter kontrolü sırasında bir hata oluştu.\n"
                    message += f"🔗 <a href='{self.tesla_url}'>Tesla Sitesini Kontrol Et</a>"
                    logger.error(f"Manual search error: {e}")
            else:
                message = "❓ <b>Bilinmeyen komut</b>\n\n"
                message += "📋 <b>/help</b> komutu ile kullanılabilir komutları görebilirsiniz."
            
            await self.send_telegram_message(message, reply_to_message_id=message_id)
            
        except Exception as e:
            logger.error(f"Error processing command {command}: {e}")
    
    async def check_messages(self):
        """Check for new messages and commands"""
        try:
            updates = await self.bot.get_updates()
            
            for update in updates:
                if update.message and update.message.text:
                    text = update.message.text.strip()
                    message_id = update.message.message_id
                    
                    # Process commands
                    if text.startswith('/'):
                        command = text.split()[0].lower()
                        await self.process_command(command, message_id)
                    
                    # Clear processed updates
                    await self.bot.get_updates(offset=update.update_id + 1)
                    
        except Exception as e:
            logger.debug(f"Error checking messages: {e}")
    
    def format_vehicle_message(self, vehicle):
        """Format vehicle information for Telegram"""
        message = f"🚗 <b>Yeni Tesla Araç!</b>\n\n"
        message += f"<b>Model:</b> {vehicle['model']}\n"
        message += f"<b>Detaylar:</b> {vehicle['details']}\n\n"
        message += f"<a href='{vehicle['url']}'>Envanteri Görüntüle</a>"
        return message
    
    async def check_inventory(self):
        """Check for new vehicles in inventory"""
        if not self.is_monitoring:
            logger.info("Monitoring is disabled, skipping inventory check")
            return
            
        logger.info("Checking Tesla inventory...")
        
        try:
            vehicles = self.get_tesla_inventory()
            current_vehicle_ids = {v['id'] for v in vehicles}
            
            # Find new vehicles
            new_vehicle_ids = current_vehicle_ids - self.last_vehicles
            
            if new_vehicle_ids:
                logger.info(f"Found {len(new_vehicle_ids)} new vehicles!")
                
                # Send notification for each new vehicle
                for vehicle in vehicles:
                    if vehicle['id'] in new_vehicle_ids:
                        message = self.format_vehicle_message(vehicle)
                        await self.send_telegram_message(message)
                        await asyncio.sleep(1)  # Avoid rate limiting
                
                # Update last known inventory
                self.last_vehicles = current_vehicle_ids
                self.save_last_inventory()
            else:
                logger.info("No new vehicles found")
                
        except Exception as e:
            logger.error(f"Error checking inventory: {e}")
    
    async def run(self):
        """Main bot loop"""
        logger.info("Tesla Envanter Bot started!")
        
        # Send startup message
        startup_message = "🤖 <b>Tesla Envanter Bot başlatıldı!</b>\n\n"
        startup_message += f"📊 <b>Takip edilen modeller:</b> {', '.join(self.models)}\n"
        startup_message += f"⏰ <b>Kontrol aralığı:</b> {self.check_interval} saniye\n"
        startup_message += f"🔄 <b>Otomatik takip:</b> {'Aktif' if self.is_monitoring else 'Pasif'}\n\n"
        startup_message += "<b>📋 Kullanılabilir Komutlar:</b>\n"
        startup_message += "/help - Yardım menüsü\n"
        startup_message += "/ping - Bot durumu\n"
        startup_message += "/manuel-arama - Manual arama\n"
        startup_message += "/durum - Detaylı durum\n\n"
        startup_message += "💡 <b>/help</b> komutu ile tüm komutları görebilirsiniz!"
        
        await self.send_telegram_message(startup_message)
        
        # Main loop
        last_message_check = 0
        message_check_interval = 5  # Check for messages every 5 seconds
        
        try:
            while True:
                try:
                    current_time = time.time()
                    
                    # Check for messages periodically
                    if current_time - last_message_check > message_check_interval:
                        await self.check_messages()
                        last_message_check = current_time
                    
                    # Check inventory
                    await self.check_inventory()
                    logger.info(f"Waiting {self.check_interval} seconds until next check...")
                    
                    # Sleep in smaller chunks to allow message checking
                    sleep_time = 0
                    while sleep_time < self.check_interval:
                        await asyncio.sleep(min(5, self.check_interval - sleep_time))
                        sleep_time += 5
                        
                        # Check messages during sleep
                        if sleep_time % message_check_interval == 0:
                            await self.check_messages()
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
        except Exception as e:
            logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    bot = TeslaInventoryBot()
    asyncio.run(bot.run())
