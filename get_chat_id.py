#!/usr/bin/env python3

import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

async def get_chat_id():
    # Load environment variables
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN bulunamadı!")
        return
    
    try:
        bot = Bot(token=token)
        
        print("🤖 Bot bilgileri alınıyor...")
        bot_info = await bot.get_me()
        print(f"✅ Bot: @{bot_info.username} ({bot_info.first_name})")
        print()
        
        print("📋 Son güncellemeleri kontrol ediliyor...")
        updates = await bot.get_updates()
        
        if not updates:
            print("❗ Henüz mesaj alınmamış!")
            print("Lütfen bot'a Telegram'dan bir mesaj gönderin ve tekrar deneyin.")
            print(f"Bot linki: https://t.me/{bot_info.username}")
        else:
            print("💬 Bulunan chat'ler:")
            chat_ids = set()
            
            for update in updates:
                if update.message:
                    chat = update.message.chat
                    chat_ids.add(chat.id)
                    
                    chat_type = "👤 Kişisel" if chat.type == "private" else f"👥 Grup ({chat.type})"
                    chat_name = chat.first_name or chat.title or "Bilinmiyor"
                    
                    print(f"  {chat_type}: {chat_name}")
                    print(f"    Chat ID: {chat.id}")
                    print()
            
            if len(chat_ids) == 1:
                chat_id = list(chat_ids)[0]
                print(f"🎯 Tek chat bulundu. Chat ID'niz: {chat_id}")
                
                # .env dosyasını güncelle
                update_env_file(chat_id)
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("Token'ın doğru olduğundan emin olun.")

def update_env_file(chat_id):
    """Update .env file with chat ID"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace the chat_id line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('TELEGRAM_CHAT_ID='):
                lines[i] = f'TELEGRAM_CHAT_ID={chat_id}'
                break
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ .env dosyası güncellendi! Chat ID: {chat_id}")
        
    except Exception as e:
        print(f"❌ .env dosyası güncellenirken hata: {e}")
        print(f"Manuel olarak ekleyin: TELEGRAM_CHAT_ID={chat_id}")

if __name__ == "__main__":
    asyncio.run(get_chat_id())
