"""
Quick Analysis Tab - One-click full pipeline execution
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from typing import Optional

from ..utils.config import ConfigManager
from ..utils.worker import ProgressWorker, run_full_pipeline_with_progress, TaskState


class QuickAnalysisTab:
    """
    Quick Analysis tab for one-click full pipeline execution.
    """
    
    def __init__(self, parent, config: ConfigManager):
        """
        Initialize quick analysis tab.
        
        Args:
            parent: Parent widget (tab frame)
            config: Configuration manager instance
        """
        self.parent = parent
        self.config = config
        self.worker: Optional[ProgressWorker] = None
        
        # State
        self.selected_files = []
        self.output_dir = config.get("default_output_dir", "")
        
        # Build UI
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all widgets for this tab"""
        # Main scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Input Section ===
        self.input_section = ctk.CTkFrame(self.scroll_frame)
        self.input_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.input_section,
            text="📂 输入设置",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # File selection
        self.file_frame = ctk.CTkFrame(self.input_section, fg_color="transparent")
        self.file_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.file_frame,
            text="CDS 文件:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.file_btn = ctk.CTkButton(
            self.file_frame,
            text="选择文件 (.ffn)",
            command=self._select_files,
            width=180
        )
        self.file_btn.pack(side="left", padx=10)
        
        self.file_count_label = ctk.CTkLabel(
            self.file_frame,
            text="未选择文件",
            text_color="gray"
        )
        self.file_count_label.pack(side="left", padx=10)
        
        # File list display
        self.file_list_label = ctk.CTkLabel(
            self.input_section,
            text="",
            wraplength=700,
            justify="left",
            text_color="gray"
        )
        self.file_list_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Output directory
        self.output_frame = ctk.CTkFrame(self.input_section, fg_color="transparent")
        self.output_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.output_entry = ctk.CTkEntry(
            self.output_frame,
            placeholder_text="选择输出目录...",
            width=400
        )
        self.output_entry.pack(side="left", padx=10, fill="x", expand=True)
        if self.output_dir:
            self.output_entry.insert(0, self.output_dir)
        
        self.output_btn = ctk.CTkButton(
            self.output_frame,
            text="浏览",
            command=self._select_output_dir,
            width=80
        )
        self.output_btn.pack(side="left", padx=(10, 0))
        
        # Bottom padding
        ctk.CTkFrame(self.input_section, height=10, fg_color="transparent").pack()
        
        # === Parameters Section ===
        self.params_section = ctk.CTkFrame(self.scroll_frame)
        self.params_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.params_section,
            text="⚙️ 分析参数",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Min CDS Length
        self.cds_frame = ctk.CTkFrame(self.params_section, fg_color="transparent")
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
        
        ctk.CTkLabel(
            self.cds_frame,
            text="bp"
        ).pack(side="left")
        
        # Tree type
        self.tree_frame = ctk.CTkFrame(self.params_section, fg_color="transparent")
        self.tree_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.tree_frame,
            text="生成树类型:",
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.tree_var = ctk.StringVar(
            value=self.config.get("default_tree_type", "both")
        )
        
        self.tree_both = ctk.CTkRadioButton(
            self.tree_frame,
            text="MST + HC",
            variable=self.tree_var,
            value="both"
        )
        self.tree_both.pack(side="left", padx=(10, 5))
        
        self.tree_mst = ctk.CTkRadioButton(
            self.tree_frame,
            text="仅 MST",
            variable=self.tree_var,
            value="mst"
        )
        self.tree_mst.pack(side="left", padx=5)
        
        self.tree_hc = ctk.CTkRadioButton(
            self.tree_frame,
            text="仅 HC",
            variable=self.tree_var,
            value="hc"
        )
        self.tree_hc.pack(side="left", padx=5)
        
        # Verbose checkbox
        self.verbose_var = ctk.BooleanVar(value=False)
        self.verbose_check = ctk.CTkCheckBox(
            self.params_section,
            text="详细输出",
            variable=self.verbose_var
        )
        self.verbose_check.pack(anchor="w", padx=15, pady=10)
        
        # Bottom padding
        ctk.CTkFrame(self.params_section, height=10, fg_color="transparent").pack()
        
        # === Progress Section ===
        self.progress_section = ctk.CTkFrame(self.scroll_frame)
        self.progress_section.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.progress_section,
            text="📊 分析进度",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_section)
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        self.progress_bar.set(0)
        
        # Progress info
        self.progress_info_frame = ctk.CTkFrame(self.progress_section, fg_color="transparent")
        self.progress_info_frame.pack(fill="x", padx=15, pady=5)
        
        self.step_label = ctk.CTkLabel(
            self.progress_info_frame,
            text="当前步骤: -",
            anchor="w"
        )
        self.step_label.pack(side="left")
        
        self.time_label = ctk.CTkLabel(
            self.progress_info_frame,
            text="预计剩余: -",
            anchor="e"
        )
        self.time_label.pack(side="right")
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.progress_section,
            text="就绪",
            text_color="gray",
            anchor="w"
        )
        self.status_label.pack(anchor="w", padx=15, pady=5)
        
        # Bottom padding
        ctk.CTkFrame(self.progress_section, height=10, fg_color="transparent").pack()
        
        # === Log Section ===
        self.log_section = ctk.CTkFrame(self.scroll_frame)
        self.log_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            self.log_section,
            text="📝 运行日志",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.log_text = ctk.CTkTextbox(self.log_section, height=150)
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # === Action Buttons ===
        self.action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.run_btn = ctk.CTkButton(
            self.action_frame,
            text="🚀 开始分析",
            command=self._run_pipeline,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.run_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.pause_btn = ctk.CTkButton(
            self.action_frame,
            text="⏸️ 暂停",
            command=self._pause_pipeline,
            height=45,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ctk.CTkButton(
            self.action_frame,
            text="⏹️ 取消",
            command=self._cancel_pipeline,
            height=45,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5)
        
    def _select_files(self):
        """Open file dialog to select FASTA files"""
        files = filedialog.askopenfilenames(
            title="选择 CDS FASTA 文件",
            filetypes=[
                ("FASTA 文件", "*.ffn *.fasta *.fa *.fna"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.selected_files = list(files)
            self.file_count_label.configure(
                text=f"已选择 {len(self.selected_files)} 个文件",
                text_color="white"
            )
            # Show first few file names
            names = [os.path.basename(f) for f in self.selected_files[:5]]
            if len(self.selected_files) > 5:
                names.append(f"... 等 {len(self.selected_files)} 个文件")
            self.file_list_label.configure(text=", ".join(names))
            
            # Save to recent
            for f in self.selected_files[:3]:
                self.config.add_recent_file(f)
                
    def _select_output_dir(self):
        """Open directory dialog to select output folder"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir = directory
            self.output_entry.delete(0, 'end')
            self.output_entry.insert(0, directory)
            self.config.add_recent_output_dir(directory)
            
    def _log(self, message: str):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def _update_progress(self, progress_info):
        """Update progress display"""
        self.progress_bar.set(progress_info.percent / 100)
        self.step_label.configure(
            text=f"当前步骤: {progress_info.step}/{progress_info.total_steps}"
        )
        
        # Format remaining time
        remaining = progress_info.estimated_remaining
        if remaining > 60:
            time_str = f"预计剩余: {remaining/60:.1f} 分钟"
        else:
            time_str = f"预计剩余: {remaining:.0f} 秒"
        self.time_label.configure(text=time_str)
        
        self.status_label.configure(text=progress_info.message)
        self._log(progress_info.message)
        
    def _run_pipeline(self):
        """Run the full CDST pipeline"""
        # Validate inputs
        if not self.selected_files:
            messagebox.showerror("错误", "请选择至少一个 FASTA 文件！")
            return
            
        output_dir = self.output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        # Get parameters
        try:
            min_cds_len = int(self.cds_entry.get())
        except ValueError:
            messagebox.showerror("错误", "最小 CDS 长度必须是数字！")
            return
            
        tree_mode = self.tree_var.get()
        verbose = self.verbose_var.get()
        
        # Clear log
        self.log_text.delete("1.0", "end")
        self._log("=" * 50)
        self._log("CDST 分析开始")
        self._log(f"输入文件: {len(self.selected_files)} 个")
        self._log(f"输出目录: {output_dir}")
        self._log(f"最小 CDS 长度: {min_cds_len} bp")
        self._log(f"树类型: {tree_mode}")
        self._log("=" * 50)
        
        # Update button states
        self.run_btn.configure(state="disabled", text="运行中...")
        self.pause_btn.configure(state="normal")
        self.cancel_btn.configure(state="normal")
        self.file_btn.configure(state="disabled")
        self.output_btn.configure(state="disabled")
        
        # Create and start worker
        self.worker = ProgressWorker(
            task_func=run_full_pipeline_with_progress,
            on_progress=self._update_progress,
            on_complete=self._on_pipeline_complete,
            on_error=self._on_pipeline_error
        )
        
        self.worker.start(
            fasta_files=self.selected_files,
            output_dir=output_dir,
            min_cds_len=min_cds_len,
            tree_mode=tree_mode,
            verbose=verbose
        )
        self.parent.after(100, self._poll_worker_events)

    def _poll_worker_events(self):
        """Process worker events on the Tk main thread."""
        if self.worker is None:
            return

        self.worker.dispatch_events()
        if self.worker.state in (TaskState.RUNNING, TaskState.PAUSED):
            self.parent.after(100, self._poll_worker_events)
        
    def _pause_pipeline(self):
        """Pause or resume the pipeline"""
        if self.worker is None:
            return
            
        if self.worker.state == TaskState.RUNNING:
            self.worker.pause()
            self.pause_btn.configure(text="▶️ 继续")
            self._log("⏸️ 分析已暂停")
        elif self.worker.state == TaskState.PAUSED:
            self.worker.resume()
            self.pause_btn.configure(text="⏸️ 暂停")
            self._log("▶️ 分析已继续")
            
    def _cancel_pipeline(self):
        """Cancel the pipeline"""
        if self.worker is None:
            return
            
        if messagebox.askyesno("确认取消", "确定要取消当前分析吗？"):
            self.worker.cancel()
            self._log("⏹️ 分析已取消")
            self._reset_ui()
            
    def _on_pipeline_complete(self, result):
        """Handle pipeline completion"""
        self._ui_pipeline_complete(result)
        
    def _ui_pipeline_complete(self, result):
        """UI update for pipeline completion"""
        self.progress_bar.set(1.0)
        self._log("=" * 50)
        self._log("✅ 分析完成！")
        self._log(f"结果保存在: {result}")
        self._log("=" * 50)
        
        self._reset_ui()
        
        messagebox.showinfo(
            "分析完成",
            f"分析已完成！\n\n结果保存在:\n{result}"
        )
        
    def _on_pipeline_error(self, error):
        """Handle pipeline error"""
        self._ui_pipeline_error(error)
        
    def _ui_pipeline_error(self, error):
        """UI update for pipeline error"""
        self._log(f"❌ 错误: {str(error)}")
        self._reset_ui()
        
        messagebox.showerror(
            "分析错误",
            f"分析过程中出现错误:\n\n{str(error)}"
        )
        
    def _reset_ui(self):
        """Reset UI to initial state"""
        self.run_btn.configure(state="normal", text="🚀 开始分析")
        self.pause_btn.configure(state="disabled", text="⏸️ 暂停")
        self.cancel_btn.configure(state="disabled")
        self.file_btn.configure(state="normal")
        self.output_btn.configure(state="normal")
        self.status_label.configure(text="就绪", text_color="gray")
