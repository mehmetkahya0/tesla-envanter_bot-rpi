#!/usr/bin/env bash

# Tesla Envanter Bot Test Script
# Bu script botu manuel olarak test etmek için kullanılabilir

echo "🚗 Tesla Envanter Bot Test Script"
echo "================================="

# .env dosyasını kontrol et ve yükle
if [ -f ".env" ]; then
    echo "📁 .env dosyası bulundu, yükleniyor..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env dosyası bulunamadı. Lütfen .env.example dosyasını .env olarak kopyalayın ve doldurun."
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Gerekli environment variables kontrol et
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN environment variable gerekli!"
    echo "Lütfen .env dosyasında TELEGRAM_BOT_TOKEN değerini doldurun."
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ TELEGRAM_CHAT_ID environment variable gerekli!"
    echo "Lütfen .env dosyasında TELEGRAM_CHAT_ID değerini doldurun."
    exit 1
fi

# Default values if not set
export CHECK_INTERVAL=${CHECK_INTERVAL:-300}
export MODELS=${MODELS:-'["Model 3", "Model Y"]'}
export DEBUG=${DEBUG:-false}
export DATA_DIR=${DATA_DIR:-./data}

echo "✅ Konfigürasyon:"
echo "   Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "   Chat ID: $TELEGRAM_CHAT_ID"
echo "   Check Interval: $CHECK_INTERVAL seconds"
echo "   Models: $MODELS"
echo "   Debug Mode: $DEBUG"
echo "   Data Directory: $DATA_DIR"
echo ""

# Data directory oluştur
mkdir -p "$DATA_DIR"

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
