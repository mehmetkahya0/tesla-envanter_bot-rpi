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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TeslaInventoryBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))
        self.models = json.loads(os.getenv('MODELS', '["Model 3", "Model Y"]'))
        
        self.bot = Bot(token=self.telegram_token)
        self.last_vehicles = set()
        self.data_file = '/app/data/last_inventory.json'
        
        # Create data directory
        os.makedirs('/app/data', exist_ok=True)
        
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Tesla Turkey inventory URL
            url = "https://www.tesla.com/tr_tr/inventory/new"
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            vehicles = []
            
            # Look for vehicle cards (Tesla's structure may change)
            vehicle_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['vehicle', 'car', 'inventory', 'product']
            ))
            
            for card in vehicle_cards:
                try:
                    # Extract vehicle information
                    model_elem = card.find(['h1', 'h2', 'h3', 'span'], string=lambda x: x and any(
                        model in str(x) for model in self.models
                    ))
                    
                    if model_elem:
                        vehicle_text = card.get_text(strip=True)
                        
                        # Create unique identifier for the vehicle
                        vehicle_id = f"{model_elem.get_text(strip=True)}_{hash(vehicle_text) % 10000}"
                        
                        vehicle_info = {
                            'id': vehicle_id,
                            'model': model_elem.get_text(strip=True),
                            'details': vehicle_text[:200],  # First 200 chars
                            'url': url
                        }
                        
                        vehicles.append(vehicle_info)
                        
                except Exception as e:
                    logger.debug(f"Error parsing vehicle card: {e}")
                    continue
            
            logger.info(f"Found {len(vehicles)} vehicles in inventory")
            return vehicles
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Tesla inventory: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    async def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info("Telegram message sent successfully")
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def format_vehicle_message(self, vehicle):
        """Format vehicle information for Telegram"""
        message = f"🚗 <b>Yeni Tesla Araç!</b>\n\n"
        message += f"<b>Model:</b> {vehicle['model']}\n"
        message += f"<b>Detaylar:</b> {vehicle['details']}\n\n"
        message += f"<a href='{vehicle['url']}'>Envanteri Görüntüle</a>"
        return message
    
    async def check_inventory(self):
        """Check for new vehicles in inventory"""
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
        startup_message = "🤖 Tesla Envanter Bot başlatıldı!\n\n"
        startup_message += f"📊 Takip edilen modeller: {', '.join(self.models)}\n"
        startup_message += f"⏰ Kontrol aralığı: {self.check_interval} saniye"
        
        await self.send_telegram_message(startup_message)
        
        while True:
            try:
                await self.check_inventory()
                logger.info(f"Waiting {self.check_interval} seconds until next check...")
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    bot = TeslaInventoryBot()
    asyncio.run(bot.run())
