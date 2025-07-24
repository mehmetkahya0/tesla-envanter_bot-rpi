#!/usr/bin/env bash

set -e

# Build configuration
BUILD_FROM="ghcr.io/home-assistant/aarch64-base:latest"
DOCKER_CLI_EXPERIMENTAL=enabled

# Build arguments
DOCKER_PUSH=true
DOCKER_CACHE=true
DOCKER_WITH_LATEST=true

# Repository configuration  
DOCKER_HUB=""
GHCR_PAT=""

# Build for multiple architectures
docker buildx create --name tesla-bot-builder --use 2>/dev/null || true

# Build and push for all supported architectures
docker buildx build \
    --platform linux/amd64,linux/arm64,linux/arm/v7 \
    --build-arg BUILD_FROM=${BUILD_FROM} \
    --tag ghcr.io/mehmetkahya/tesla-envanter-bot:latest \
    --tag ghcr.io/mehmetkahya/tesla-envanter-bot:1.0.0 \
    ${DOCKER_PUSH:+--push} \
    .

echo "Build completed successfully!"
