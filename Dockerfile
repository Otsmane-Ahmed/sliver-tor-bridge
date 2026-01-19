FROM python:3.10-slim

# Install Tor
RUN apt-get update && apt-get install -y \
    tor \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Expose the hidden service port (internal)
EXPOSE 8080

# Default command
CMD ["sliver-tor-bridge", "start", "--sliver-host", "host.docker.internal"]
