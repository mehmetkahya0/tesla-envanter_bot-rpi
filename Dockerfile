ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM $BUILD_FROM

# Install Python and required packages
RUN \
    apk add --no-cache \
        python3 \
        python3-dev \
        py3-pip \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY tesla_bot.py .
COPY run.sh .

# Make run script executable
RUN chmod a+x /app/run.sh

# Create data directory
RUN mkdir -p /app/data

# Run the application
CMD ["/app/run.sh"]
