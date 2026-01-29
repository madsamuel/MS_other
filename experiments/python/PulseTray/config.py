"""Configuration management for PulseTray"""
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Handle application configuration."""
    
    DEFAULT_CONFIG = {
        "poll_interval": 1.0,  # seconds
        "cpu_alert": 85,  # percent
        "memory_alert": 80,  # percent
        "disk_alert": 90,  # percent
        "history_minutes": 10,
        "alert_duration_seconds": 10,  # how long to trigger alert for CPU
        "show_notifications": True,
        "monitoring_enabled": True,
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration from file or defaults."""
        if config_path is None:
            config_path = Path.home() / ".pulsetray" / "config.json"
        
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                    self.data.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}. Using defaults.")
        else:
            self.save()  # Create default config
    
    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set and save a configuration value."""
        self.data[key] = value
        self.save()
