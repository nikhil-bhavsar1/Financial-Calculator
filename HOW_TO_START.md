# How to Start the Financial Calculator Desktop App

## Prerequisites

Make sure the Vite development server is running first:

```bash
# In Terminal 1 - Start Vite (if not already running)
npm run dev
```

Wait until you see:
```
VITE v6.x.x  ready in XXX ms
➜  Local:   http://localhost:1420/
```

## Starting the Desktop App

### Option 1: Using the Launch Script (Easiest)

```bash
# In Terminal 2
./launch-desktop.sh
```

### Option 2: Manual Command with Wayland

Modern GNU/Linux systems use Wayland:

```bash
# In Terminal 2 - Using Wayland (recommended)
GDK_BACKEND=wayland WEBKIT_DISABLE_COMPOSITING_MODE=1 npm run tauri dev
```

Or if you're on an older system with X11:

```bash
# In Terminal 2 - Using X11 (fallback)
GDK_BACKEND=x11 WEBKIT_DISABLE_COMPOSITING_MODE=1 npm run tauri dev
```

The launch script automatically detects and uses the correct backend.

### Option 3: Using the Interactive Script

```bash
./start.sh
```

This will:
1. Check if Vite is running
2. Open the web version in your browser
3. Ask if you want to launch the desktop app

## What to Expect

When you run the command, you should see:

1. **In the terminal:**
   ```
   Running DevCommand (`cargo run --no-default-features --color always --`)
   Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.XX s
   Running `target/debug/financial-calculator`
   ```

2. **On your screen:**
   - A new window titled "Financial Calculator" should appear
   - It should load the same interface as http://localhost:1420

## Troubleshooting

### If the window doesn't appear:
- Check your taskbar/dock
- Try Alt+Tab to cycle through windows
- The window might be on another workspace

### If the window is blank or frozen:
- Press Ctrl+C in the terminal to stop
- Use the web version instead: http://localhost:1420
- The web version has identical functionality

### If you see "GBM buffer" error:
- The environment variables should fix this
- If not, use the web version

### If you see "port 1420 already in use":
- This is normal - Vite is already running
- Just continue with the desktop app launch

## Quick Reference

| What | Command |
|------|---------|
| Start Vite only | `npm run dev` |
| Start desktop app | `./launch-desktop.sh` |
| Start everything | `./start.sh` |
| Stop desktop app | Press `Ctrl+C` in the terminal |
| Use web version | Open http://localhost:1420 in browser |

## Current Status

To check what's running:

```bash
# Check Vite server
curl -I http://localhost:1420

# Check desktop app process
ps aux | grep financial-calculator

# List all windows
wmctrl -l
```
