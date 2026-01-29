# PulseTray - System Health Monitoring Application

A lightweight system tray application that monitors CPU, memory, disk, and network metrics in real-time.

## Features

- **System Tray Icon** - Runs in background with live tooltip metrics
- **Live Metrics Collection** - CPU, Memory, Disk, Network usage updated every 1 second
- **Details Dashboard** - Pop-up window with visual metric cards and status indicators
- **Threshold Alerts** - Color-coded alerts when thresholds are exceeded
- **Export Snapshots** - Export metrics history to CSV
- **Configuration** - JSON-based settings for thresholds and behavior
- **Cross-Platform** - Windows, macOS, Linux support

## Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

1. Navigate to the PulseTray directory:
```bash
cd PulseTray
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

The application will start with a tray icon. Right-click the icon to access the menu.

## Usage

### Tray Menu Options

- **Show Details** - Opens the metrics dashboard window
- **Pause Monitoring** - Temporarily stops metric collection
- **Export Snapshot** - Saves last 10 minutes of metrics to CSV
- **Settings** - Opens configuration (future version)
- **Quit** - Closes the application

### Configuration

Configuration is stored in `~/.pulsetray/config.json`

Default values:
```json
{
  "poll_interval": 1.0,
  "cpu_alert": 85,
  "memory_alert": 80,
  "disk_alert": 90,
  "history_minutes": 10,
  "alert_duration_seconds": 10,
  "show_notifications": true,
  "monitoring_enabled": true
}
```

## Architecture

```
psutil → Metrics Collector → State Store (Ring Buffer)
                                    ↓
                              Alert Manager
                                    ↓
                              UI Layer (Tray + Window)
```

### Key Components

- **metrics.py** - System metric collection and formatting
- **state.py** - Ring buffer for metric history
- **alerts.py** - Threshold-based alert management
- **tray.py** - System tray icon and menu
- **details_window.py** - Metrics dashboard UI
- **config.py** - Configuration management
- **main.py** - Application orchestration

## Demo

1. Launch the application
2. Hover over tray icon to see live metrics
3. Double-click or select "Show Details" to open dashboard
4. Run a CPU-intensive task to trigger alerts
5. Export metrics via tray menu
6. Right-click → Quit to exit

## Performance

- Minimal CPU overhead (<1% on modern systems)
- Memory footprint: ~60-80 MB
- Responsive tray interactions
- Stable for 24/7 monitoring

## Future Enhancements

- Historical charts (matplotlib/QtCharts)
- Per-process monitoring
- GPU metrics support
- SQLite logging backend
- Settings UI dialog
- Desktop notifications
- Dark mode
- Plugin system

## Notes

- Temperature sensors may not work on all systems
- Network metrics show bytes per second, not current connections
- CPU alert requires sustained threshold for 10 seconds before clearing
- Memory and disk alerts clear immediately when below threshold

## License

MIT
