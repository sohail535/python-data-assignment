FROM python:3.12-slim

USER root

WORKDIR /app

# Install system dependencies, Java, and Chrome
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-21-jdk-headless \
    chromium \
    chromium-driver \
    gcc \
    python3-dev \
    libpq-dev \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome and ChromeDriver environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONPATH=/app

# Set Java home for PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/bronze /app/data/silver /app/data/gold

CMD ["python", "-m", "orchestration.prefect.flow"]
