#!/bin/bash

# Start Xvfb
Xvfb :99 -ac -screen 0 1280x1024x16 &
export DISPLAY=:99

# Start Fluxbox window manager
fluxbox &

# Start VNC server without password
x11vnc -forever -shared -no6 -nopw -create &

# Start noVNC
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &

# Run your Python script
python /app/src/main.py https://google.com 'search for todays hong kong weather'
