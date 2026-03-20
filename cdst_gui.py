"""
CDST GUI Application - Desktop interface for CoDing Sequence Typer
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys

from cdst import core
import pandas as pd


class CDSTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CDST - CoDing Sequence Typer")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Store selected files and settings
        self.selected_files = []
        self.output_dir = ""
        self.min_cds_len = 201
        self.tree_mode = "both"
        self.verbose = False
        
        # Create main layout
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="CoDing Sequence Typer (CDST)",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # Scrollable content frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_frame.pack(fill="both", expand=True, pady=10)
        
        # File Selection Section
        self.file_section = ctk.CTkFrame(self.scroll_frame)
        self.file_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.file_section, 
            text="Input FASTA Files",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.file_btn = ctk.CTkButton(
            self.file_section,
            text="Select FASTA Files (.ffn)",
            command=self.select_files,
            width=200
        )
        self.file_btn.pack(anchor="w", pady=5)
        
        self.file_list_label = ctk.CTkLabel(
            self.file_section,
            text="No files selected",
            text_color="gray",
            wraplength=600,
            justify="left"
        )
        self.file_list_label.pack(anchor="w", pady=5)
        
        # Output Directory Section
        self.output_section = ctk.CTkFrame(self.scroll_frame)
        self.output_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.output_section,
            text="Output Directory",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.output_frame = ctk.CTkFrame(self.output_section, fg_color="transparent")
        self.output_frame.pack(fill="x", pady=5)
        
        self.output_entry = ctk.CTkEntry(self.output_frame, placeholder_text="Select output directory...", width=400)
        self.output_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.output_btn = ctk.CTkButton(
            self.output_frame,
            text="Browse",
            command=self.select_output_dir,
            width=100
        )
        self.output_btn.pack(side="left")
        
        # Settings Section
        self.settings_section = ctk.CTkFrame(self.scroll_frame)
        self.settings_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.settings_section,
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        # Min CDS Length
        self.cds_frame = ctk.CTkFrame(self.settings_section, fg_color="transparent")
        self.cds_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.cds_frame,
            text="Minimum CDS Length:",
            width=200,
            anchor="w"
        ).pack(side="left")
        
        self.cds_entry = ctk.CTkEntry(self.cds_frame, width=100)
        self.cds_entry.insert(0, "201")
        self.cds_entry.pack(side="left", padx=10)
        
        # Tree Mode
        self.tree_frame = ctk.CTkFrame(self.settings_section, fg_color="transparent")
        self.tree_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            self.tree_frame,
            text="Tree Type:",
            width=200,
            anchor="w"
        ).pack(side="left")
        
        self.tree_var = ctk.StringVar(value="both")
        self.tree_menu = ctk.CTkOptionMenu(
            self.tree_frame,
            variable=self.tree_var,
            values=["mst", "hc", "both"],
            width=150
        )
        self.tree_menu.pack(side="left", padx=10)
        
        # Verbose checkbox
        self.verbose_var = ctk.BooleanVar(value=False)
        self.verbose_check = ctk.CTkCheckBox(
            self.settings_section,
            text="Verbose Output",
            variable=self.verbose_var
        )
        self.verbose_check.pack(anchor="w", pady=10)
        
        # Progress Section
        self.progress_section = ctk.CTkFrame(self.scroll_frame)
        self.progress_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.progress_section,
            text="Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_section)
        self.progress_bar.pack(fill="x", pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_section,
            text="Ready",
            text_color="gray"
        )
        self.status_label.pack(anchor="w", pady=5)
        
        # Log/Output text area
        self.log_label = ctk.CTkLabel(
            self.progress_section,
            text="Log Output:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(self.progress_section, height=150)
        self.log_text.pack(fill="x", pady=5)
        
        # Run Button
        self.run_btn = ctk.CTkButton(
            self.main_frame,
            text="Run Full Pipeline",
            command=self.run_pipeline,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            fg_color="green"
        )
        self.run_btn.pack(pady=20)
        
    def select_files(self):
        """Open file dialog to select FASTA files"""
        files = filedialog.askopenfilenames(
            title="Select CDS FASTA Files",
            filetypes=[("FASTA files", "*.ffn *.fasta *.fa *.fna"), ("All files", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            file_names = [os.path.basename(f) for f in self.selected_files]
            self.file_list_label.configure(
                text=f"Selected {len(self.selected_files)} file(s):\n" + ", ".join(file_names),
                text_color="white"
            )
            
    def select_output_dir(self):
        """Open directory dialog to select output folder"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_entry.delete(0, 'end')
            self.output_entry.insert(0, directory)
            
    def log(self, message):
        """Add message to log text area"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        
    def update_status(self, status, progress=None):
        """Update status label and progress bar"""
        self.status_label.configure(text=status)
        if progress is not None:
            self.progress_bar.set(progress)
            
    def run_pipeline(self):
        """Run the full CDST pipeline in a separate thread"""
        # Validate inputs
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one FASTA file!")
            return
            
        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output directory!")
            return
            
        # Get settings
        try:
            self.min_cds_len = int(self.cds_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Minimum CDS Length must be a number!")
            return
            
        self.tree_mode = self.tree_var.get()
        self.verbose = self.verbose_var.get()
        
        # Disable run button during execution
        self.run_btn.configure(state="disabled", text="Running...")
        self.log_text.delete("1.0", "end")
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._run_pipeline_thread)
        thread.daemon = True
        thread.start()
        
    def _run_pipeline_thread(self):
        """Execute pipeline in background thread"""
        try:
            self.update_status("Starting pipeline...", 0.1)
            self.log("=" * 50)
            self.log("CDST Pipeline Started")
            self.log("=" * 50)
            
            # Run the full pipeline
            core.run_full_pipeline(
                fasta_files=self.selected_files,
                output_dir=self.output_dir,
                min_cds_len=self.min_cds_len,
                tree_mode=self.tree_mode,
                verbose=self.verbose
            )
            
            self.update_status("Pipeline completed successfully!", 1.0)
            self.log("=" * 50)
            self.log("Pipeline completed successfully!")
            self.log(f"Results saved to: {self.output_dir}")
            self.log("=" * 50)
            
            # Show completion message
            self.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Pipeline completed!\n\nResults saved to:\n{self.output_dir}"
            ))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.update_status("Error occurred!", 0)
            self.log(error_msg)
            self.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Re-enable run button
            self.after(0, lambda: self.run_btn.configure(state="normal", text="Run Full Pipeline"))


if __name__ == "__main__":
    app = CDSTApp()
    app.mainloop()
