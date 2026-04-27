"""
Database Management Tab - Merge databases and compare samples
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
import threading
from typing import List

from ..utils.config import ConfigManager


class DatabaseManagerTab:
    """Database management tab for merging and comparing databases."""
    
    def __init__(self, parent, config: ConfigManager):
        self.parent = parent
        self.config = config
        self.selected_databases = []
        self.new_samples = []
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for database management"""
        # Main scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Merge Databases Section ===
        self.merge_section = ctk.CTkFrame(self.scroll_frame)
        self.merge_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.merge_section,
            text="📚 合并数据库",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Database list
        ctk.CTkLabel(
            self.merge_section,
            text="选择要合并的数据库:",
            anchor="w"
        ).pack(anchor="w", padx=15, pady=5)
        
        self.db_list_frame = ctk.CTkFrame(self.merge_section)
        self.db_list_frame.pack(fill="x", padx=15, pady=5)
        
        self.db_listbox = ctk.CTkTextbox(self.db_list_frame, height=100)
        self.db_listbox.pack(fill="x", padx=5, pady=5)
        
        # Buttons
        self.db_btn_frame = ctk.CTkFrame(self.merge_section, fg_color="transparent")
        self.db_btn_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(
            self.db_btn_frame,
            text="➕ 添加数据库",
            command=self._add_database,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.db_btn_frame,
            text="➖ 移除选中",
            command=self._remove_database,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.db_btn_frame,
            text="🗑️ 清空列表",
            command=self._clear_databases,
            width=120
        ).pack(side="left", padx=5)
        
        # Merge options
        self.merge_options_frame = ctk.CTkFrame(self.merge_section, fg_color="transparent")
        self.merge_options_frame.pack(fill="x", padx=15, pady=10)
        
        self.merge_matrix_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.merge_options_frame,
            text="同时合并距离矩阵（如果存在）",
            variable=self.merge_matrix_var
        ).pack(anchor="w", pady=2)
        
        self.merge_mst_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.merge_options_frame,
            text="生成合并后的 MST",
            variable=self.merge_mst_var
        ).pack(anchor="w", pady=2)
        
        # Output directory
        self.merge_output_frame = ctk.CTkFrame(self.merge_section, fg_color="transparent")
        self.merge_output_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.merge_output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.merge_output_entry = ctk.CTkEntry(
            self.merge_output_frame,
            placeholder_text="选择输出目录...",
            width=350
        )
        self.merge_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.merge_output_frame,
            text="浏览",
            command=lambda: self._select_output_dir(self.merge_output_entry),
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Merge button
        ctk.CTkButton(
            self.merge_section,
            text="🔄 开始合并",
            command=self._merge_databases,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        ).pack(anchor="w", padx=15, pady=15)
        
        # Padding
        ctk.CTkFrame(self.merge_section, height=10, fg_color="transparent").pack()
        
        # === Compare Samples Section ===
        self.compare_section = ctk.CTkFrame(self.scroll_frame)
        self.compare_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.compare_section,
            text="🔍 比较新样本",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Reference database
        self.ref_db_frame = ctk.CTkFrame(self.compare_section, fg_color="transparent")
        self.ref_db_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.ref_db_frame,
            text="参考数据库:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.ref_db_entry = ctk.CTkEntry(
            self.ref_db_frame,
            placeholder_text="选择参考数据库 JSON 文件...",
            width=350
        )
        self.ref_db_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.ref_db_frame,
            text="浏览",
            command=self._select_reference_db,
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # New samples
        self.new_samples_frame = ctk.CTkFrame(self.compare_section, fg_color="transparent")
        self.new_samples_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.new_samples_frame,
            text="新样本文件:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkButton(
            self.new_samples_frame,
            text="选择文件",
            command=self._select_new_samples,
            width=120
        ).pack(side="left", padx=10)
        
        self.new_samples_label = ctk.CTkLabel(
            self.new_samples_frame,
            text="未选择",
            text_color="gray"
        )
        self.new_samples_label.pack(side="left", padx=10)
        
        # Output directory
        self.compare_output_frame = ctk.CTkFrame(self.compare_section, fg_color="transparent")
        self.compare_output_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.compare_output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.compare_output_entry = ctk.CTkEntry(
            self.compare_output_frame,
            placeholder_text="选择输出目录...",
            width=350
        )
        self.compare_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.compare_output_frame,
            text="浏览",
            command=lambda: self._select_output_dir(self.compare_output_entry),
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Compare button
        ctk.CTkButton(
            self.compare_section,
            text="🔍 开始比较",
            command=self._compare_samples,
            fg_color="blue",
            hover_color="darkblue",
            width=150
        ).pack(anchor="w", padx=15, pady=15)
        
        # Padding
        ctk.CTkFrame(self.compare_section, height=10, fg_color="transparent").pack()
        
        # === Log Section ===
        self.log_section = ctk.CTkFrame(self.scroll_frame)
        self.log_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.log_section,
            text="📝 运行日志",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(self.log_section, height=120)
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
    def _log(self, message: str):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def _select_output_dir(self, entry_widget):
        """Select output directory"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, directory)
            
    def _add_database(self):
        """Add database to list"""
        files = filedialog.askopenfilenames(
            title="选择数据库 JSON 文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if files:
            for file in files:
                if file not in self.selected_databases:
                    self.selected_databases.append(file)
            self._update_database_list()
            
    def _remove_database(self):
        """Remove selected database"""
        # Simple implementation: remove last added
        if self.selected_databases:
            self.selected_databases.pop()
            self._update_database_list()
            
    def _clear_databases(self):
        """Clear all databases"""
        self.selected_databases = []
        self._update_database_list()
        
    def _update_database_list(self):
        """Update database list display"""
        self.db_listbox.delete("1.0", "end")
        for i, db in enumerate(self.selected_databases, 1):
            self.db_listbox.insert("end", f"{i}. {os.path.basename(db)}\n")
            
    def _select_reference_db(self):
        """Select reference database"""
        file = filedialog.askopenfilename(
            title="选择参考数据库 JSON 文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if file:
            self.ref_db_entry.delete(0, 'end')
            self.ref_db_entry.insert(0, file)
            
    def _select_new_samples(self):
        """Select new sample files"""
        files = filedialog.askopenfilenames(
            title="选择新样本 FASTA 文件",
            filetypes=[
                ("FASTA 文件", "*.ffn *.fasta *.fa *.fna"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.new_samples = list(files)
            self.new_samples_label.configure(
                text=f"已选择 {len(self.new_samples)} 个文件",
                text_color="white"
            )
            
    def _merge_databases(self):
        """Merge selected databases"""
        if not self.selected_databases:
            messagebox.showerror("错误", "请至少选择一个数据库！")
            return
            
        output_dir = self.merge_output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        self._log(f"开始合并 {len(self.selected_databases)} 个数据库...")

        input_dirs = [os.path.dirname(path) for path in self.selected_databases]
        generate_matrix = self.merge_matrix_var.get()
        generate_mst = self.merge_mst_var.get()

        def run_merge():
            try:
                from cdst import core

                outputs = core.join_databases(
                    input_dirs,
                    output_dir,
                    generate_matrix=generate_matrix,
                    generate_mst=generate_mst,
                    verbose=True,
                )
                self.parent.after(0, self._merge_complete, outputs)
            except Exception as e:
                self.parent.after(0, self._task_error, "数据库合并", e)

        threading.Thread(target=run_merge, daemon=True).start()
        
    def _compare_samples(self):
        """Compare new samples against reference database"""
        ref_db = self.ref_db_entry.get().strip()
        if not ref_db or not os.path.exists(ref_db):
            messagebox.showerror("错误", "请选择有效的参考数据库！")
            return
            
        if not self.new_samples:
            messagebox.showerror("错误", "请选择新样本文件！")
            return
            
        output_dir = self.compare_output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        self._log(f"开始比较 {len(self.new_samples)} 个新样本...")

        def run_compare():
            try:
                from cdst import core

                outputs = core.test_new_samples(
                    self.new_samples,
                    ref_db,
                    output_dir,
                    min_cds_len=self.config.get("min_cds_len", 201),
                    verbose=True,
                )
                self.parent.after(0, self._compare_complete, outputs)
            except Exception as e:
                self.parent.after(0, self._task_error, "样本比较", e)

        threading.Thread(target=run_compare, daemon=True).start()

    def _merge_complete(self, outputs):
        """Handle database merge completion."""
        self._log("✅ 数据库合并完成")
        for label, path in outputs.items():
            self._log(f"  {label}: {path}")
        messagebox.showinfo("完成", f"数据库合并完成！\n\n结果保存在:\n{self.merge_output_entry.get().strip()}")

    def _compare_complete(self, outputs):
        """Handle sample comparison completion."""
        self._log("✅ 样本比较完成")
        for label, path in outputs.items():
            self._log(f"  {label}: {path}")
        messagebox.showinfo("完成", f"样本比较完成！\n\n结果保存在:\n{self.compare_output_entry.get().strip()}")

    def _task_error(self, task_name, error):
        """Show task errors."""
        self._log(f"❌ {task_name}失败: {error}")
        messagebox.showerror(f"{task_name}错误", f"{task_name}过程中出现错误:\n\n{error}")
