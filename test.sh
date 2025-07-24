#!/usr/bin/env bash

# Tesla Envanter Bot Test Script
# Bu script botu manuel olarak test etmek için kullanılabilir

echo "🚗 Tesla Envanter Bot Test Script"
echo "================================="

# Gerekli environment variables kontrol et
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN environment variable gerekli!"
    echo "Kullanım: TELEGRAM_BOT_TOKEN=your_token TELEGRAM_CHAT_ID=your_chat_id ./test.sh"
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ TELEGRAM_CHAT_ID environment variable gerekli!"
    echo "Kullanım: TELEGRAM_BOT_TOKEN=your_token TELEGRAM_CHAT_ID=your_chat_id ./test.sh"
    exit 1
fi

# Default values
export CHECK_INTERVAL=60
export MODELS='["Model 3", "Model Y"]'

echo "✅ Konfigürasyon:"
echo "   Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "   Chat ID: $TELEGRAM_CHAT_ID"
echo "   Check Interval: $CHECK_INTERVAL seconds"
echo "   Models: $MODELS"
echo ""

# Python dependencies kontrol et
echo "📦 Python dependencies kontrol ediliyor..."
python3 -c "import requests, bs4, telegram, asyncio" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Tüm dependencies mevcut"
else
    echo "❌ Bazı dependencies eksik. Yükleniyor..."
    pip3 install -r requirements.txt
fi

echo ""
echo "🚀 Bot başlatılıyor..."
echo "Durdurmak için Ctrl+C kullanın"
echo ""

# Bot'u başlat
python3 tesla_bot.py
