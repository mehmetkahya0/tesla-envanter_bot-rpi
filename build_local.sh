#!/usr/bin/env bash

echo "🚀 Tesla Envanter Bot - Local Home Assistant Add-on Builder"
echo "=========================================================="

# Check if we're on ARM64 (Apple Silicon) or AMD64
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    HA_ARCH="aarch64"
    BASE_IMAGE="ghcr.io/home-assistant/aarch64-base:latest"
elif [[ "$ARCH" == "x86_64" ]]; then
    HA_ARCH="amd64"
    BASE_IMAGE="ghcr.io/home-assistant/amd64-base:latest"
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

echo "🔍 Detected architecture: $ARCH -> Home Assistant: $HA_ARCH"
echo "📦 Base image: $BASE_IMAGE"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker build \
    --build-arg BUILD_FROM="$BASE_IMAGE" \
    --tag "local/tesla-envanter-bot:latest" \
    --tag "local/tesla-envanter-bot:1.0.0" \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully!"
    echo ""
    echo "📋 Next steps for Home Assistant:"
    echo "1. Copy this entire folder to your Home Assistant addons directory:"
    echo "   /usr/share/hassio/addons/local/tesla-envanter-bot/"
    echo ""
    echo "2. Or use the Samba/SSH add-on to upload:"
    echo "   /config/addons/tesla-envanter-bot/"
    echo ""
    echo "3. Restart Home Assistant Supervisor"
    echo "4. Go to Supervisor > Add-on Store > Local Add-ons"
    echo "5. Install Tesla Envanter Bot"
    echo ""
    echo "🏷️  Image tags created:"
    echo "   - local/tesla-envanter-bot:latest"
    echo "   - local/tesla-envanter-bot:1.0.0"
else
    echo ""
    echo "❌ Docker build failed!"
    exit 1
fi
