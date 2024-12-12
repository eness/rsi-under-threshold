# Use a Python-based Docker image
FROM python:3.9-slim

# Install system dependencies and TA-Lib C library
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr && make && make install \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Upgrade pip and setuptools
RUN python -m pip install --upgrade pip setuptools wheel

# Copy and install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command (no copying of main.py)
CMD ["python", "/app/main.py"]
