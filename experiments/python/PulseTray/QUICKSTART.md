# PulseTray Quick Start Guide

## One-Minute Setup

### Windows, macOS, or Linux

```bash
cd PulseTray
python setup.py
```

This will:
1. Install dependencies (psutil, PySide6)
2. Run validation tests
3. Start the application

### Manual Setup (if preferred)

```bash
cd PulseTray
pip install -r requirements.txt
python main.py
```

## What You'll See

When you run the app:
- A small colored circle icon appears in your system tray
- Right-click it to see the menu
- Hover over it to see live metrics:
  - CPU: X.X%
  - Memory: X.X%
  - Disk: X.X%
  - Network speeds

## Demo in 3 Minutes

1. **Launch** (10 seconds)
   ```bash
   python setup.py
   ```
   Wait for tray icon to appear in the system tray.

2. **View Live Metrics** (30 seconds)
   - Hover over the tray icon to see the tooltip with live CPU, memory, disk, and network metrics
   - Metrics update every 1 second

3. **Open Dashboard** (30 seconds)
   - Double-click the tray icon OR
   - Right-click → "Show Details"
   - You'll see visual cards with:
     - CPU usage percentage
     - Memory usage percentage
     - Disk usage percentage
     - Network upload/download speeds
     - Color-coded status (green/yellow/red)

4. **Trigger an Alert** (1 minute)
   - Open a resource-heavy application (video encoding, compilation, etc.)
   - Watch the CPU or memory card turn red
   - The tray icon will turn red
   - Close the app to clear the alert

5. **Export Metrics** (30 seconds)
   - Right-click tray → "Export Snapshot"
   - A CSV file is saved to your home directory
   - Contains last 10 minutes of metrics

6. **Cleanup** (10 seconds)
   - Right-click → "Quit"
   - App closes cleanly

## Keyboard Shortcuts

- Double-click tray icon = Show Details window
- Right-click tray icon = Show menu

## Configuration

Edit `~/.pulsetray/config.json` to customize:

```json
{
  "poll_interval": 1.0,        # Update frequency in seconds
  "cpu_alert": 85,             # CPU alert threshold (%)
  "memory_alert": 80,          # Memory alert threshold (%)
  "disk_alert": 90,            # Disk alert threshold (%)
  "history_minutes": 10,       # How long to keep history
  "alert_duration_seconds": 10 # How long CPU alert stays active
}
```

## Troubleshooting

### "PySide6 not found"
```bash
pip install PySide6
```

### "psutil not found"
```bash
pip install psutil
```

### Application won't start
Run the test first to diagnose:
```bash
python test_setup.py
```

### No tray icon appears
- On Linux, you may need a tray-compatible desktop environment
- Try Ubuntu with GNOME or KDE Plasma

## Features

- ✓ Real-time system monitoring
- ✓ Visual dashboard with color-coded alerts
- ✓ Metric history (ring buffer)
- ✓ CSV export
- ✓ Configurable thresholds
- ✓ Minimal resource usage
- ✓ Cross-platform (Windows, macOS, Linux)

## Next Steps

After getting comfortable with the basic features:
1. Explore the configuration options
2. Check the exported CSV files to understand the data format
3. Review the main.py code to understand the architecture
4. Consider enhancements like:
   - Historical charts
   - Per-process monitoring
   - Custom alerts

---

**Questions?** Check README.md for full documentation.
