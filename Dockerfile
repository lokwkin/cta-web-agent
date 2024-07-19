FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    chromium \
    fonts-noto-color-emoji \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    libgbm1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install noVNC and websockify
RUN mkdir -p /opt/novnc \
    && wget -qO- https://github.com/novnc/noVNC/archive/v1.2.0.tar.gz | tar xz --strip 1 -C /opt/novnc \
    && mkdir -p /opt/novnc/utils/websockify \
    && wget -qO- https://github.com/novnc/websockify/archive/v0.10.0.tar.gz | tar xz --strip 1 -C /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN playwright install
RUN playwright install-deps

# Set environment variable to use system Chromium
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# Copy the current directory contents into the container at /app
COPY . /app

# Expose VNC and noVNC ports
EXPOSE 5900 6080


# Copy the startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set the entrypoint to our startup script
ENTRYPOINT ["/start.sh"]