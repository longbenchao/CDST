"""
Configuration management for CDST GUI
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """
    User configuration manager for CDST GUI.
    Handles saving and loading user preferences.
    """
    
    DEFAULT_CONFIG = {
        # General settings
        "theme": "dark",
        "language": "zh_CN",
        "default_output_dir": "",
        "auto_save_config": True,
        
        # Analysis parameters
        "min_cds_len": 201,
        "default_tree_type": "both",  # "mst", "hc", or "both"
        "enable_parallel": True,
        "thread_count": "auto",  # "auto" or specific number
        
        # Visualization settings
        "image_format": "png",  # "png", "pdf", "svg"
        "image_dpi": 300,
        "image_width": 800,
        "image_height": 600,
        "color_scheme": "viridis",  # matplotlib colormap
        
        # History settings
        "save_history": True,
        "max_history": 50,
        
        # Recent files
        "recent_files": [],
        "recent_output_dirs": []
    }
    
    def __init__(self):
        """Initialize configuration manager"""
        self.config_dir = Path.home() / ".cdst"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        If file doesn't exist, return default configuration.
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (to handle new config keys)
                    return {**self.DEFAULT_CONFIG, **loaded}
            except Exception as e:
                print(f"[Config] Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
        
    def save_config(self):
        """Save current configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any, auto_save: bool = True):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            auto_save: Whether to automatically save to file
        """
        self.config[key] = value
        if auto_save and self.config.get("auto_save_config", True):
            self.save_config()
            
    def update(self, updates: Dict[str, Any], auto_save: bool = True):
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of key-value pairs to update
            auto_save: Whether to automatically save to file
        """
        self.config.update(updates)
        if auto_save and self.config.get("auto_save_config", True):
            self.save_config()
            
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        
    def add_recent_file(self, file_path: str, max_items: int = 10):
        """
        Add a file to recent files list.
        
        Args:
            file_path: Path to add
            max_items: Maximum number of recent items to keep
        """
        recent = self.config.get("recent_files", [])
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
            
        # Add to front
        recent.insert(0, file_path)
        
        # Trim to max size
        recent = recent[:max_items]
        
        self.set("recent_files", recent)
        
    def add_recent_output_dir(self, dir_path: str, max_items: int = 10):
        """
        Add an output directory to recent list.
        
        Args:
            dir_path: Directory path to add
            max_items: Maximum number of recent items to keep
        """
        recent = self.config.get("recent_output_dirs", [])
        
        # Remove if already exists
        if dir_path in recent:
            recent.remove(dir_path)
            
        # Add to front
        recent.insert(0, dir_path)
        
        # Trim to max size
        recent = recent[:max_items]
        
        self.set("recent_output_dirs", recent)
        
    def clear_history(self):
        """Clear all recent files and directories"""
        self.config["recent_files"] = []
        self.config["recent_output_dirs"] = []
        self.save_config()


# Global config instance
_config_instance = None

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
