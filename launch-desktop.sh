#!/bin/bash

# Tauri Desktop App Launcher - Modern Wayland Graphics
echo "Launching Financial Calculator Desktop App..."

# Use Wayland (modern GNU/Linux graphics standard)
export GDK_BACKEND=wayland
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1

# WebKit optimizations for Wayland
export WEBKIT_DISABLE_COMPOSITING_MODE=1
export WEBKIT_DISABLE_DMABUF_RENDERER=1

# Fallback to X11 if Wayland is not available
if [ -z "$WAYLAND_DISPLAY" ] && [ -n "$DISPLAY" ]; then
    echo "⚠️  Wayland not detected, falling back to X11"
    export GDK_BACKEND=x11
fi

# Ensure Vite is running
if ! lsof -Pi :1420 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Error: Vite server is not running on port 1420"
    echo "Please run 'npm run dev' in another terminal first"
    exit 1
fi

echo "✓ Vite server detected on port 1420"
echo "✓ Using graphics backend: $GDK_BACKEND"
echo "Starting Tauri desktop application..."

# Launch Tauri
npm run tauri dev
