"""
Main window for CDST GUI
"""

import customtkinter as ctk
import os
import sys

# Import configuration and logger
from .utils.config import get_config
from .utils.logger import get_logger


class MainWindow(ctk.CTk):
    """
    Main application window for CDST GUI.
    Implements a tabbed interface with 5 main sections.
    """
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        # Load configuration
        self.config = get_config()
        self.logger = get_logger()
        
        # Setup window
        self.title("CDST - CoDing Sequence Typer")
        self.geometry("1400x900")
        self.minsize(1100, 760)
        
        # Set appearance mode and color theme
        theme = self.config.get("theme", "dark")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Create main layout
        self._create_menu_bar()
        self._create_tab_view()
        self._create_status_bar()
        
        # Center window on screen
        self._center_window()
        
    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_menu_bar(self):
        """Create menu bar"""
        # Note: customtkinter doesn't have native menu support,
        # so we'll create a custom menu bar using buttons
        self.menu_frame = ctk.CTkFrame(self, height=40)
        self.menu_frame.pack(fill="x", padx=0, pady=0)
        
        # File menu
        self.file_menu = ctk.CTkButton(
            self.menu_frame,
            text="文件",
            width=80,
            command=self._show_file_menu
        )
        self.file_menu.pack(side="left", padx=5, pady=5)
        
        # Settings menu
        self.settings_menu = ctk.CTkButton(
            self.menu_frame,
            text="设置",
            width=80,
            command=self._show_settings_menu
        )
        self.settings_menu.pack(side="left", padx=5, pady=5)
        
        # Help menu
        self.help_menu = ctk.CTkButton(
            self.menu_frame,
            text="帮助",
            width=80,
            command=self._show_help_menu
        )
        self.help_menu.pack(side="left", padx=5, pady=5)
        
    def _create_tab_view(self):
        """Create tabbed view"""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_view.add("快速分析")
        self.tab_view.add("分步执行")
        self.tab_view.add("数据库管理")
        self.tab_view.add("结果查看")
        self.tab_view.add("设置")
        
        # Import and create tab content
        self._create_quick_analysis_tab()
        self._create_step_by_step_tab()
        self._create_database_tab()
        self._create_results_tab()
        self._create_settings_tab()
        
    def _create_quick_analysis_tab(self):
        """Create quick analysis tab content"""
        from .tabs.quick_analysis import QuickAnalysisTab
        self.quick_analysis = QuickAnalysisTab(
            self.tab_view.tab("快速分析"),
            self.config
        )
        
    def _create_step_by_step_tab(self):
        """Create step-by-step execution tab content"""
        from .tabs.step_by_step import StepByStepTab
        self.step_by_step = StepByStepTab(
            self.tab_view.tab("分步执行"),
            self.config
        )
        
    def _create_database_tab(self):
        """Create database management tab content"""
        from .tabs.database_manager import DatabaseManagerTab
        self.database_manager = DatabaseManagerTab(
            self.tab_view.tab("数据库管理"),
            self.config
        )
        
    def _create_results_tab(self):
        """Create results viewer tab content"""
        from .tabs.results_viewer import ResultsViewerTab
        self.results_viewer = ResultsViewerTab(
            self.tab_view.tab("结果查看"),
            self.config
        )
        
    def _create_settings_tab(self):
        """Create settings tab content"""
        from .tabs.settings import SettingsTab
        self.settings = SettingsTab(
            self.tab_view.tab("设置"),
            self.config
        )
        
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.pack(fill="x", padx=0, pady=0)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # System info
        self.sys_info_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            anchor="e"
        )
        self.sys_info_label.pack(side="right", padx=10, pady=5)
        
        # Update system info periodically
        self._update_system_info()
        
    def _update_system_info(self):
        """Update system information in status bar"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            mem_used = memory.used / (1024**3)  # GB
            self.sys_info_label.configure(
                text=f"CPU: {cpu_percent:.1f}% | 内存: {mem_used:.1f}GB"
            )
        except Exception:
            self.sys_info_label.configure(text="")
            
        # Schedule next update
        self.after(5000, self._update_system_info)
        
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_label.configure(text=message)
        
    def _show_file_menu(self):
        """Show file menu options"""
        # Create a simple dropdown menu (customtkinter limitation)
        # For now, just show a dialog
        from tkinter import messagebox
        messagebox.showinfo("文件", "文件菜单功能：\n• 新建项目\n• 打开项目\n• 保存配置\n• 退出")
        
    def _show_settings_menu(self):
        """Show settings menu options"""
        # Switch to settings tab
        self.tab_view.set("设置")
        
    def _show_help_menu(self):
        """Show help menu options"""
        from tkinter import messagebox
        help_text = """CDST - CoDing Sequence Typer
        
版本: 0.3.0

CDST 是一个细菌基因组分型和聚类工具。

主要功能：
• 基于 MD5 哈希的 CDS 序列分析
• 最小生成树 (MST) 构建
• 层次聚类 (HC) 分析
• 结果可视化

更多信息请访问：
https://github.com/l1-mh/CDST
        """
        messagebox.showinfo("帮助", help_text)


def main():
    """Main entry point for CDST GUI"""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
