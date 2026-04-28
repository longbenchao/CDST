"""
Logger utility for CDST GUI
"""

import datetime
import os
from typing import Optional


class GuiLogger:
    """
    Logger for CDST GUI that outputs to both console and GUI log widget.
    """
    
    def __init__(self, log_widget=None):
        """
        Initialize logger.
        
        Args:
            log_widget: CTkTextbox widget for displaying logs
        """
        self.log_widget = log_widget
        self.log_file = None
        
    def set_widget(self, log_widget):
        """Set the log display widget"""
        self.log_widget = log_widget
        
    def set_log_file(self, log_path: str):
        """Set a file path for logging"""
        self.log_file = log_path
        
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        print(formatted)
        
        # Write to log widget
        if self.log_widget is not None:
            try:
                self.log_widget.insert("end", formatted + "\n")
                self.log_widget.see("end")
            except Exception:
                pass
                
        # Write to log file
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(formatted + "\n")
            except Exception:
                pass
                
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
        
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")
        
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")
        
    def debug(self, message: str):
        """Log debug message"""
        self.log(message, "DEBUG")
        
    def success(self, message: str):
        """Log success message"""
        self.log(message, "SUCCESS")
        
    def clear(self):
        """Clear the log widget"""
        if self.log_widget is not None:
            try:
                self.log_widget.delete("1.0", "end")
            except Exception:
                pass


# Global logger instance
_logger_instance = None

def get_logger() -> GuiLogger:
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = GuiLogger()
    return _logger_instance
