"""
Settings Tab - User preferences and configuration
"""

import customtkinter as ctk
from tkinter import messagebox

from ..utils.config import ConfigManager


class SettingsTab:
    """Settings tab for user preferences."""
    
    def __init__(self, parent, config: ConfigManager):
        self.parent = parent
        self.config = config
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for settings"""
        # Main scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === General Settings ===
        self.general_section = ctk.CTkFrame(self.scroll_frame)
        self.general_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.general_section,
            text="⚙️ 通用设置",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Theme
        self.theme_frame = ctk.CTkFrame(self.general_section, fg_color="transparent")
        self.theme_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.theme_frame,
            text="主题:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.config.get("theme", "dark"))
        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.theme_var,
            values=["dark", "light", "system"],
            width=150
        )
        self.theme_menu.pack(side="left", padx=10)
        
        # Default output directory
        self.default_output_frame = ctk.CTkFrame(self.general_section, fg_color="transparent")
        self.default_output_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.default_output_frame,
            text="默认输出目录:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.default_output_entry = ctk.CTkEntry(
            self.default_output_frame,
            placeholder_text="留空则每次手动选择",
            width=300
        )
        self.default_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        default_dir = self.config.get("default_output_dir", "")
        if default_dir:
            self.default_output_entry.insert(0, default_dir)
        
        # Auto save config
        self.auto_save_var = ctk.BooleanVar(
            value=self.config.get("auto_save_config", True)
        )
        ctk.CTkCheckBox(
            self.general_section,
            text="自动保存配置",
            variable=self.auto_save_var
        ).pack(anchor="w", padx=15, pady=10)
        
        # Padding
        ctk.CTkFrame(self.general_section, height=10, fg_color="transparent").pack()
        
        # === Analysis Parameters ===
        self.analysis_section = ctk.CTkFrame(self.scroll_frame)
        self.analysis_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.analysis_section,
            text="🧬 分析参数默认值",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Min CDS Length
        self.cds_frame = ctk.CTkFrame(self.analysis_section, fg_color="transparent")
        self.cds_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.cds_frame,
            text="最小 CDS 长度:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.cds_entry = ctk.CTkEntry(self.cds_frame, width=100)
        self.cds_entry.insert(0, str(self.config.get("min_cds_len", 201)))
        self.cds_entry.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.cds_frame, text="bp").pack(side="left")
        
        # Default tree type
        self.tree_frame = ctk.CTkFrame(self.analysis_section, fg_color="transparent")
        self.tree_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.tree_frame,
            text="默认树类型:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.tree_var = ctk.StringVar(
            value=self.config.get("default_tree_type", "both")
        )
        self.tree_menu = ctk.CTkOptionMenu(
            self.tree_frame,
            variable=self.tree_var,
            values=["both", "mst", "hc"],
            width=150
        )
        self.tree_menu.pack(side="left", padx=10)
        
        # Padding
        ctk.CTkFrame(self.analysis_section, height=10, fg_color="transparent").pack()
        
        # === Visualization Settings ===
        self.viz_section = ctk.CTkFrame(self.scroll_frame)
        self.viz_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.viz_section,
            text="📊 可视化设置",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Image format
        self.format_frame = ctk.CTkFrame(self.viz_section, fg_color="transparent")
        self.format_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.format_frame,
            text="默认图片格式:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.format_var = ctk.StringVar(
            value=self.config.get("image_format", "png")
        )
        self.format_menu = ctk.CTkOptionMenu(
            self.format_frame,
            variable=self.format_var,
            values=["png", "pdf", "svg"],
            width=150
        )
        self.format_menu.pack(side="left", padx=10)
        
        # Image DPI
        self.dpi_frame = ctk.CTkFrame(self.viz_section, fg_color="transparent")
        self.dpi_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.dpi_frame,
            text="图片分辨率:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.dpi_var = ctk.StringVar(
            value=str(self.config.get("image_dpi", 300))
        )
        self.dpi_menu = ctk.CTkOptionMenu(
            self.dpi_frame,
            variable=self.dpi_var,
            values=["150", "200", "300", "600"],
            width=150
        )
        self.dpi_menu.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.dpi_frame, text="DPI").pack(side="left")
        
        # Color scheme
        self.color_frame = ctk.CTkFrame(self.viz_section, fg_color="transparent")
        self.color_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.color_frame,
            text="颜色方案:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.color_var = ctk.StringVar(
            value=self.config.get("color_scheme", "viridis")
        )
        self.color_menu = ctk.CTkOptionMenu(
            self.color_frame,
            variable=self.color_var,
            values=["viridis", "plasma", "inferno", "magma", "cividis", "coolwarm"],
            width=150
        )
        self.color_menu.pack(side="left", padx=10)
        
        # Padding
        ctk.CTkFrame(self.viz_section, height=10, fg_color="transparent").pack()
        
        # === History Settings ===
        self.history_section = ctk.CTkFrame(self.scroll_frame)
        self.history_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.history_section,
            text="📝 历史记录",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Save history
        self.save_history_var = ctk.BooleanVar(
            value=self.config.get("save_history", True)
        )
        ctk.CTkCheckBox(
            self.history_section,
            text="保存历史记录",
            variable=self.save_history_var
        ).pack(anchor="w", padx=15, pady=5)
        
        # Max history
        self.max_history_frame = ctk.CTkFrame(self.history_section, fg_color="transparent")
        self.max_history_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.max_history_frame,
            text="最大历史数:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.max_history_entry = ctk.CTkEntry(self.max_history_frame, width=100)
        self.max_history_entry.insert(0, str(self.config.get("max_history", 50)))
        self.max_history_entry.pack(side="left", padx=10)
        
        # Clear history button
        ctk.CTkButton(
            self.history_section,
            text="🗑️ 清除历史",
            command=self._clear_history,
            width=120
        ).pack(anchor="w", padx=15, pady=10)
        
        # Padding
        ctk.CTkFrame(self.history_section, height=10, fg_color="transparent").pack()
        
        # === Action Buttons ===
        self.action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            self.action_frame,
            text="💾 保存设置",
            command=self._save_settings,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        ).pack(side="left", padx=10, pady=15)
        
        ctk.CTkButton(
            self.action_frame,
            text="🔄 恢复默认",
            command=self._reset_defaults,
            fg_color="red",
            hover_color="darkred",
            width=150
        ).pack(side="left", padx=10, pady=15)
        
    def _save_settings(self):
        """Save current settings"""
        try:
            updates = {
                "theme": self.theme_var.get(),
                "default_output_dir": self.default_output_entry.get().strip(),
                "auto_save_config": self.auto_save_var.get(),
                "min_cds_len": int(self.cds_entry.get()),
                "default_tree_type": self.tree_var.get(),
                "image_format": self.format_var.get(),
                "image_dpi": int(self.dpi_var.get()),
                "color_scheme": self.color_var.get(),
                "save_history": self.save_history_var.get(),
                "max_history": int(self.max_history_entry.get()),
            }
            
            self.config.update(updates)
            
            # Apply theme
            ctk.set_appearance_mode(updates["theme"])
            
            messagebox.showinfo("成功", "设置已保存！")
            
        except ValueError as e:
            messagebox.showerror("错误", f"设置值无效: {e}")
            
    def _reset_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            self.config.reset_to_defaults()
            messagebox.showinfo("成功", "已恢复默认设置！\n请重启应用以生效。")
            
    def _clear_history(self):
        """Clear history"""
        if messagebox.askyesno("确认", "确定要清除所有历史记录吗？"):
            self.config.clear_history()
            messagebox.showinfo("成功", "历史记录已清除！")
