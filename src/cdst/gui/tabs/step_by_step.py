"""
Step-by-Step Execution Tab - Run each pipeline step individually
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
import threading
from typing import Optional

from ..utils.config import ConfigManager
from ..utils.worker import ProgressWorker, TaskState


class StepByStepTab:
    """
    Step-by-step execution tab for running individual pipeline steps.
    """
    
    def __init__(self, parent, config: ConfigManager):
        """
        Initialize step-by-step tab.
        
        Args:
            parent: Parent widget (tab frame)
            config: Configuration manager instance
        """
        self.parent = parent
        self.config = config
        
        # State tracking
        self.step1_completed = False  # Generate MD5 hashes
        self.step2_completed = False  # Compute matrices
        self.step3_completed = False  # Generate trees
        
        # Intermediate results
        self.md5_json_path = ""
        self.diff_matrix_path = ""
        self.comp_matrix_path = ""
        
        # Workers
        self.current_worker: Optional[ProgressWorker] = None
        
        # Build UI
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all widgets for this tab"""
        # Main scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Workflow Progress Indicator ===
        self.workflow_frame = ctk.CTkFrame(self.scroll_frame)
        self.workflow_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(
            self.workflow_frame,
            text="工作流程",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Step indicators
        self.indicator_frame = ctk.CTkFrame(self.workflow_frame, fg_color="transparent")
        self.indicator_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.step1_indicator = ctk.CTkLabel(
            self.indicator_frame,
            text="① 生成哈希",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.step1_indicator.pack(side="left", padx=5, expand=True)
        
        ctk.CTkLabel(
            self.indicator_frame,
            text="→",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=5)
        
        self.step2_indicator = ctk.CTkLabel(
            self.indicator_frame,
            text="② 计算矩阵",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.step2_indicator.pack(side="left", padx=5, expand=True)
        
        ctk.CTkLabel(
            self.indicator_frame,
            text="→",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=5)
        
        self.step3_indicator = ctk.CTkLabel(
            self.indicator_frame,
            text="③ 生成树",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.step3_indicator.pack(side="left", padx=5, expand=True)
        
        # === Step 1: Generate MD5 Hashes ===
        self.step1_frame = ctk.CTkFrame(self.scroll_frame)
        self.step1_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Step 1 header
        self.step1_header = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        self.step1_header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.step1_status = ctk.CTkLabel(
            self.step1_header,
            text="○",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        self.step1_status.pack(side="left")
        
        ctk.CTkLabel(
            self.step1_header,
            text="  Step 1: 生成 MD5 哈希",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Step 1 content
        self.step1_content = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        self.step1_content.pack(fill="x", padx=30, pady=5)
        
        # Input files
        self.s1_file_frame = ctk.CTkFrame(self.step1_content, fg_color="transparent")
        self.s1_file_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s1_file_frame,
            text="输入文件:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s1_file_btn = ctk.CTkButton(
            self.s1_file_frame,
            text="选择文件 (.ffn)",
            command=self._select_step1_files,
            width=150
        )
        self.s1_file_btn.pack(side="left", padx=10)
        
        self.s1_file_label = ctk.CTkLabel(
            self.s1_file_frame,
            text="未选择",
            text_color="gray"
        )
        self.s1_file_label.pack(side="left", padx=10)
        
        # Min CDS length
        self.s1_param_frame = ctk.CTkFrame(self.step1_content, fg_color="transparent")
        self.s1_param_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s1_param_frame,
            text="最小 CDS 长度:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s1_cds_entry = ctk.CTkEntry(self.s1_param_frame, width=100)
        self.s1_cds_entry.insert(0, str(self.config.get("min_cds_len", 201)))
        self.s1_cds_entry.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.s1_param_frame, text="bp").pack(side="left")
        
        # Output directory
        self.s1_output_frame = ctk.CTkFrame(self.step1_content, fg_color="transparent")
        self.s1_output_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s1_output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s1_output_entry = ctk.CTkEntry(
            self.s1_output_frame,
            placeholder_text="选择输出目录...",
            width=350
        )
        self.s1_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.s1_output_frame,
            text="浏览",
            command=lambda: self._select_output_dir(self.s1_output_entry),
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Step 1 execute button
        self.s1_run_btn = ctk.CTkButton(
            self.step1_content,
            text="▶ 执行此步骤",
            command=self._run_step1,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        )
        self.s1_run_btn.pack(anchor="w", pady=10)
        
        # Step 1 results preview
        self.s1_result_label = ctk.CTkLabel(
            self.step1_content,
            text="",
            text_color="gray"
        )
        self.s1_result_label.pack(anchor="w", pady=5)
        
        # Padding
        ctk.CTkFrame(self.step1_frame, height=10, fg_color="transparent").pack()
        
        # === Step 2: Compute Matrices ===
        self.step2_frame = ctk.CTkFrame(self.scroll_frame)
        self.step2_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Step 2 header
        self.step2_header = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        self.step2_header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.step2_status = ctk.CTkLabel(
            self.step2_header,
            text="○",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        self.step2_status.pack(side="left")
        
        ctk.CTkLabel(
            self.step2_header,
            text="  Step 2: 计算距离矩阵",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Step 2 content
        self.step2_content = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        self.step2_content.pack(fill="x", padx=30, pady=5)
        
        # JSON file input
        self.s2_json_frame = ctk.CTkFrame(self.step2_content, fg_color="transparent")
        self.s2_json_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s2_json_frame,
            text="JSON 文件:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s2_json_entry = ctk.CTkEntry(
            self.s2_json_frame,
            placeholder_text="选择 MD5 哈希 JSON 文件...",
            width=350
        )
        self.s2_json_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.s2_json_frame,
            text="浏览",
            command=self._select_json_file,
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Auto-load button
        self.s2_auto_btn = ctk.CTkButton(
            self.s2_json_frame,
            text="自动加载",
            command=self._auto_load_json,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.s2_auto_btn.pack(side="left", padx=5)
        
        # Output directory
        self.s2_output_frame = ctk.CTkFrame(self.step2_content, fg_color="transparent")
        self.s2_output_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s2_output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s2_output_entry = ctk.CTkEntry(
            self.s2_output_frame,
            placeholder_text="选择输出目录...",
            width=350
        )
        self.s2_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.s2_output_frame,
            text="浏览",
            command=lambda: self._select_output_dir(self.s2_output_entry),
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Step 2 execute button
        self.s2_run_btn = ctk.CTkButton(
            self.step2_content,
            text="▶ 执行此步骤",
            command=self._run_step2,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        )
        self.s2_run_btn.pack(anchor="w", pady=10)
        
        # Step 2 results preview
        self.s2_result_label = ctk.CTkLabel(
            self.step2_content,
            text="",
            text_color="gray"
        )
        self.s2_result_label.pack(anchor="w", pady=5)
        
        # Padding
        ctk.CTkFrame(self.step2_frame, height=10, fg_color="transparent").pack()
        
        # === Step 3: Generate Trees ===
        self.step3_frame = ctk.CTkFrame(self.scroll_frame)
        self.step3_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Step 3 header
        self.step3_header = ctk.CTkFrame(self.step3_frame, fg_color="transparent")
        self.step3_header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.step3_status = ctk.CTkLabel(
            self.step3_header,
            text="○",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        ).pack(side="left")
        
        ctk.CTkLabel(
            self.step3_header,
            text="  Step 3: 生成系统发育树",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Step 3 content
        self.step3_content = ctk.CTkFrame(self.step3_frame, fg_color="transparent")
        self.step3_content.pack(fill="x", padx=30, pady=5)
        
        # Matrix file input
        self.s3_matrix_frame = ctk.CTkFrame(self.step3_content, fg_color="transparent")
        self.s3_matrix_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s3_matrix_frame,
            text="矩阵文件:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s3_matrix_entry = ctk.CTkEntry(
            self.s3_matrix_frame,
            placeholder_text="选择差异矩阵 CSV 文件...",
            width=350
        )
        self.s3_matrix_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.s3_matrix_frame,
            text="浏览",
            command=self._select_matrix_file,
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Auto-load button
        ctk.CTkButton(
            self.s3_matrix_frame,
            text="自动加载",
            command=self._auto_load_matrix,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=5)
        
        # Tree type
        self.s3_tree_frame = ctk.CTkFrame(self.step3_content, fg_color="transparent")
        self.s3_tree_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s3_tree_frame,
            text="树类型:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s3_tree_var = ctk.StringVar(
            value=self.config.get("default_tree_type", "both")
        )
        
        ctk.CTkRadioButton(
            self.s3_tree_frame,
            text="MST + HC",
            variable=self.s3_tree_var,
            value="both"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            self.s3_tree_frame,
            text="仅 MST",
            variable=self.s3_tree_var,
            value="mst"
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            self.s3_tree_frame,
            text="仅 HC",
            variable=self.s3_tree_var,
            value="hc"
        ).pack(side="left", padx=5)
        
        # Output directory
        self.s3_output_frame = ctk.CTkFrame(self.step3_content, fg_color="transparent")
        self.s3_output_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.s3_output_frame,
            text="输出目录:",
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.s3_output_entry = ctk.CTkEntry(
            self.s3_output_frame,
            placeholder_text="选择输出目录...",
            width=350
        )
        self.s3_output_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            self.s3_output_frame,
            text="浏览",
            command=lambda: self._select_output_dir(self.s3_output_entry),
            width=80
        ).pack(side="left", padx=(10, 0))
        
        # Step 3 execute button
        self.s3_run_btn = ctk.CTkButton(
            self.step3_content,
            text="▶ 执行此步骤",
            command=self._run_step3,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        )
        self.s3_run_btn.pack(anchor="w", pady=10)
        
        # Step 3 results preview
        self.s3_result_label = ctk.CTkLabel(
            self.step3_content,
            text="",
            text_color="gray"
        )
        self.s3_result_label.pack(anchor="w", pady=5)
        
        # Padding
        ctk.CTkFrame(self.step3_frame, height=10, fg_color="transparent").pack()
        
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
        
    def _select_step1_files(self):
        """Select input files for step 1"""
        files = filedialog.askopenfilenames(
            title="选择 CDS FASTA 文件",
            filetypes=[
                ("FASTA 文件", "*.ffn *.fasta *.fa *.fna"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.s1_files = list(files)
            self.s1_file_label.configure(
                text=f"已选择 {len(self.s1_files)} 个文件",
                text_color="white"
            )
            
    def _select_output_dir(self, entry_widget):
        """Select output directory and update entry widget"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, directory)
            
    def _select_json_file(self):
        """Select JSON file for step 2"""
        file = filedialog.askopenfilename(
            title="选择 MD5 哈希 JSON 文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if file:
            self.s2_json_entry.delete(0, 'end')
            self.s2_json_entry.insert(0, file)
            
    def _select_matrix_file(self):
        """Select matrix file for step 3"""
        file = filedialog.askopenfilename(
            title="选择差异矩阵 CSV 文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file:
            self.s3_matrix_entry.delete(0, 'end')
            self.s3_matrix_entry.insert(0, file)
            
    def _auto_load_json(self):
        """Auto-load JSON from step 1 output"""
        if self.md5_json_path and os.path.exists(self.md5_json_path):
            self.s2_json_entry.delete(0, 'end')
            self.s2_json_entry.insert(0, self.md5_json_path)
            self._log(f"已自动加载: {self.md5_json_path}")
        else:
            messagebox.showinfo("提示", "请先完成 Step 1 以生成 JSON 文件")
            
    def _auto_load_matrix(self):
        """Auto-load matrix from step 2 output"""
        if self.diff_matrix_path and os.path.exists(self.diff_matrix_path):
            self.s3_matrix_entry.delete(0, 'end')
            self.s3_matrix_entry.insert(0, self.diff_matrix_path)
            self._log(f"已自动加载: {self.diff_matrix_path}")
        else:
            messagebox.showinfo("提示", "请先完成 Step 2 以生成差异矩阵")
            
    def _update_step_indicators(self):
        """Update step indicator colors"""
        if self.step1_completed:
            self.step1_indicator.configure(text_color="green")
            self.step1_status.configure(text="✓", text_color="green")
        if self.step2_completed:
            self.step2_indicator.configure(text_color="green", font=ctk.CTkFont(size=14, weight="bold"))
            self.step2_status.configure(text="✓", text_color="green")
        if self.step3_completed:
            self.step3_indicator.configure(text_color="green", font=ctk.CTkFont(size=14, weight="bold"))
            self.step3_status.configure(text="✓", text_color="green")
            
    def _run_step1(self):
        """Run step 1: Generate MD5 hashes"""
        from cdst import core
        
        # Validate
        if not hasattr(self, 's1_files') or not self.s1_files:
            messagebox.showerror("错误", "请选择输入文件！")
            return
            
        output_dir = self.s1_output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        try:
            min_cds_len = int(self.s1_cds_entry.get())
        except ValueError:
            messagebox.showerror("错误", "最小 CDS 长度必须是数字！")
            return
            
        self._log("Step 1: 开始生成 MD5 哈希...")
        self.s1_run_btn.configure(state="disabled", text="运行中...")
        
        def run_step1():
            try:
                os.makedirs(output_dir, exist_ok=True)
                md5_dict = {}
                for i, fasta_file in enumerate(self.s1_files):
                    md5_dict[fasta_file] = core.generate_md5_for_fasta(
                        fasta_file, min_cds_len=min_cds_len, verbose=True
                    )
                    self.after(0, lambda i=i: self._log(
                        f"  处理文件 {i+1}/{len(self.s1_files)}: {os.path.basename(self.s1_files[i])}"
                    ))
                    
                json_output_path = os.path.join(output_dir, "md5_hashes.json")
                with open(json_output_path, "w") as f:
                    json.dump(md5_dict, f, indent=4)
                    
                self.md5_json_path = json_output_path
                self.step1_completed = True
                
                # Calculate stats
                total_hashes = sum(len(v) for v in md5_dict.values())
                unique_hashes = len(set(h for v in md5_dict.values() for h in v))
                
                self.after(0, self._step1_complete, total_hashes, unique_hashes, json_output_path)
                
            except Exception as e:
                self.after(0, self._step_error, "Step 1", e)
                
        thread = threading.Thread(target=run_step1, daemon=True)
        thread.start()
        
    def _step1_complete(self, total_hashes, unique_hashes, json_path):
        """Handle step 1 completion"""
        self._log(f"✅ Step 1 完成！生成 {total_hashes} 个哈希，其中 {unique_hashes} 个唯一")
        self.s1_run_btn.configure(state="normal", text="▶ 执行此步骤")
        self.s1_result_label.configure(
            text=f"✅ 已生成: {total_hashes} 个哈希 | {unique_hashes} 个唯一 | 保存至: {os.path.basename(json_path)}",
            text_color="green"
        )
        
        # Auto-fill step 2
        self.s2_json_entry.delete(0, 'end')
        self.s2_json_entry.insert(0, json_path)
        
        # Auto-fill output dir for step 2
        output_dir = self.s1_output_entry.get().strip()
        if output_dir:
            self.s2_output_entry.delete(0, 'end')
            self.s2_output_entry.insert(0, output_dir)
            
        self._update_step_indicators()
        
    def _run_step2(self):
        """Run step 2: Compute matrices"""
        from cdst import core
        import pandas as pd
        
        json_path = self.s2_json_entry.get().strip()
        if not json_path or not os.path.exists(json_path):
            messagebox.showerror("错误", "请选择有效的 JSON 文件！")
            return
            
        output_dir = self.s2_output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        self._log("Step 2: 开始计算距离矩阵...")
        self.s2_run_btn.configure(state="disabled", text="运行中...")
        
        def run_step2():
            try:
                with open(json_path, "r") as f:
                    md5_dict = json.load(f)
                    
                self.after(0, lambda: self._log("  正在计算比较矩阵..."))
                comparison_matrix = core.generate_comparison_matrix(md5_dict, verbose=True)
                
                os.makedirs(output_dir, exist_ok=True)
                comp_path = os.path.join(output_dir, "comparison_matrix.csv")
                comparison_matrix.to_csv(comp_path)
                
                self.after(0, lambda: self._log("  正在计算差异矩阵..."))
                diff_matrix = core.calculate_difference_matrix(comparison_matrix)
                diff_path = os.path.join(output_dir, "difference_matrix.csv")
                diff_matrix.to_csv(diff_path)
                
                self.comp_matrix_path = comp_path
                self.diff_matrix_path = diff_path
                self.step2_completed = True
                
                n_samples = len(comparison_matrix)
                self.after(0, self._step2_complete, n_samples, comp_path, diff_path)
                
            except Exception as e:
                self.after(0, self._step_error, "Step 2", e)
                
        thread = threading.Thread(target=run_step2, daemon=True)
        thread.start()
        
    def _step2_complete(self, n_samples, comp_path, diff_path):
        """Handle step 2 completion"""
        self._log(f"✅ Step 2 完成！已计算 {n_samples} 个样本的距离矩阵")
        self.s2_run_btn.configure(state="normal", text="▶ 执行此步骤")
        self.s2_result_label.configure(
            text=f"✅ 已计算: {n_samples} 个样本 | 保存至: {os.path.basename(diff_path)}",
            text_color="green"
        )
        
        # Auto-fill step 3
        self.s3_matrix_entry.delete(0, 'end')
        self.s3_matrix_entry.insert(0, self.diff_matrix_path)
        
        output_dir = self.s2_output_entry.get().strip()
        if output_dir:
            self.s3_output_entry.delete(0, 'end')
            self.s3_output_entry.insert(0, output_dir)
            
        self._update_step_indicators()
        
    def _run_step3(self):
        """Run step 3: Generate trees"""
        from cdst import core
        import pandas as pd
        
        matrix_path = self.s3_matrix_entry.get().strip()
        if not matrix_path or not os.path.exists(matrix_path):
            messagebox.showerror("错误", "请选择有效的差异矩阵文件！")
            return
            
        output_dir = self.s3_output_entry.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录！")
            return
            
        tree_mode = self.s3_tree_var.get()
        
        self._log(f"Step 3: 开始生成系统发育树 ({tree_mode})...")
        self.s3_run_btn.configure(state="disabled", text="运行中...")
        
        def run_step3():
            try:
                diff_matrix = pd.read_csv(matrix_path, index_col=0)
                os.makedirs(output_dir, exist_ok=True)
                
                result_files = []
                
                if tree_mode in ("mst", "both"):
                    self.after(0, lambda: self._log("  正在生成 MST..."))
                    edge_list = core.generate_edge_list(diff_matrix)
                    mst_edges = core.generate_mst(edge_list)
                    
                    mst_csv = os.path.join(output_dir, "mst.csv")
                    with open(mst_csv, "w") as f:
                        f.write("Node1,Node2,Distance\n")
                        for u, v, data in mst_edges:
                            f.write(f"{u},{v},{data['weight']}\n")
                            
                    newick_str = core.mst_to_newick(mst_edges, list(diff_matrix.index))
                    mst_newick = os.path.join(output_dir, "mst.newick")
                    with open(mst_newick, "w") as f:
                        f.write(newick_str)
                        
                    result_files.extend(["mst.csv", "mst.newick"])
                    
                if tree_mode in ("hc", "both"):
                    self.after(0, lambda: self._log("  正在生成 HC 树..."))
                    hc_tree = core.generate_hc_tree(diff_matrix)
                    leaf_names = list(diff_matrix.index)
                    newick_str = core.tree_to_newick(hc_tree, "", hc_tree.dist, leaf_names)
                    hc_newick = os.path.join(output_dir, "hc.newick")
                    with open(hc_newick, "w") as f:
                        f.write(newick_str)
                        
                    result_files.append("hc.newick")
                    
                self.step3_completed = True
                self.after(0, self._step3_complete, result_files, output_dir)
                
            except Exception as e:
                self.after(0, self._step_error, "Step 3", e)
                
        thread = threading.Thread(target=run_step3, daemon=True)
        thread.start()
        
    def _step3_complete(self, result_files, output_dir):
        """Handle step 3 completion"""
        self._log(f"✅ Step 3 完成！生成文件: {', '.join(result_files)}")
        self.s3_run_btn.configure(state="normal", text="▶ 执行此步骤")
        self.s3_result_label.configure(
            text=f"✅ 已生成: {', '.join(result_files)} | 保存至: {output_dir}",
            text_color="green"
        )
        self._update_step_indicators()
        
    def _step_error(self, step_name, error):
        """Handle step execution error"""
        self._log(f"❌ {step_name} 错误: {str(error)}")
        
        # Reset button states
        if step_name == "Step 1":
            self.s1_run_btn.configure(state="normal", text="▶ 执行此步骤")
        elif step_name == "Step 2":
            self.s2_run_btn.configure(state="normal", text="▶ 执行此步骤")
        elif step_name == "Step 3":
            self.s3_run_btn.configure(state="normal", text="▶ 执行此步骤")
            
        messagebox.showerror(f"{step_name} 错误", f"执行过程中出现错误:\n\n{str(error)}")
