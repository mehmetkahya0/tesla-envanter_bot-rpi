ARG BUILD_FROM=alpine:3.19
FROM $BUILD_FROM

# Install Python and required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    tzdata \
    curl

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application files
COPY tesla_bot.py .
COPY run.sh .

# Make run script executable
RUN chmod a+x /app/run.sh

# Create data directory
RUN mkdir -p /app/data

# Run the application
CMD ["/app/run.sh"]
