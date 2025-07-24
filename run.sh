#!/usr/bin/with-contenv bashio

# Get configuration
TELEGRAM_BOT_TOKEN=$(bashio::config 'telegram_bot_token')
TELEGRAM_CHAT_ID=$(bashio::config 'telegram_chat_id')
CHECK_INTERVAL=$(bashio::config 'check_interval')
MODELS=$(bashio::config 'models')

# Validate required configuration
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    bashio::log.fatal "Telegram bot token is required!"
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    bashio::log.fatal "Telegram chat ID is required!"
    exit 1
fi

bashio::log.info "Starting Tesla Envanter Bot..."
bashio::log.info "Check interval: ${CHECK_INTERVAL} seconds"

# Export environment variables
export TELEGRAM_BOT_TOKEN
export TELEGRAM_CHAT_ID
export CHECK_INTERVAL
export MODELS

# Start the Python application
python3 /app/tesla_bot.py
