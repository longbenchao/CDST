"""
Background worker for CDST GUI with progress tracking
"""

import threading
import time
import queue
from typing import Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TaskState(Enum):
    """Task execution state"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressInfo:
    """Progress information for a running task"""
    step: int = 0
    total_steps: int = 0
    percent: float = 0.0
    message: str = ""
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0


class ProgressWorker:
    """
    Background task executor with progress tracking, pause, and cancel support.
    
    Usage:
        worker = ProgressWorker(task_function, on_progress, on_complete)
        worker.start()
        
        # Later...
        worker.cancel()
    """
    
    def __init__(
        self,
        task_func: Callable,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """
        Initialize worker.
        
        Args:
            task_func: Function to execute. Must accept progress_callback parameter.
            on_progress: Called with ProgressInfo when progress updates
            on_complete: Called with result when task completes
            on_error: Called with exception when task fails
        """
        self.task_func = task_func
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        
        self._state = TaskState.PENDING
        self._thread: Optional[threading.Thread] = None
        self._start_time: float = 0
        self._pause_event = threading.Event()
        self._cancel_flag = False
        self._progress = ProgressInfo()
        self._events = queue.Queue()
        
        # Set pause event by default (not paused)
        self._pause_event.set()
        
    @property
    def state(self) -> TaskState:
        """Get current task state"""
        return self._state
        
    @property
    def progress(self) -> ProgressInfo:
        """Get current progress info"""
        return self._progress

    def dispatch_events(self):
        """
        Dispatch queued worker events.

        Call this from the Tk main thread, for example via widget.after().
        """
        while True:
            try:
                event_type, payload = self._events.get_nowait()
            except queue.Empty:
                break

            if event_type == "progress" and self.on_progress:
                self.on_progress(payload)
            elif event_type == "complete" and self.on_complete:
                self.on_complete(payload)
            elif event_type == "error" and self.on_error:
                self.on_error(payload)
        
    def start(self, *args, **kwargs):
        """
        Start the task in a background thread.
        
        Args are passed to task_func along with progress_callback.
        """
        if self._state == TaskState.RUNNING:
            return
            
        self._state = TaskState.RUNNING
        self._cancel_flag = False
        self._start_time = time.time()
        self._pause_event.set()
        
        self._thread = threading.Thread(
            target=self._run_task,
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        self._thread.start()
        
    def pause(self):
        """Pause the task"""
        if self._state == TaskState.RUNNING:
            self._state = TaskState.PAUSED
            self._pause_event.clear()
            
    def resume(self):
        """Resume a paused task"""
        if self._state == TaskState.PAUSED:
            self._state = TaskState.RUNNING
            self._pause_event.set()
            
    def cancel(self):
        """Request task cancellation"""
        self._cancel_flag = True
        self._state = TaskState.CANCELLED
        # Unpause if paused so thread can exit
        self._pause_event.set()
        
    def _should_pause(self) -> bool:
        """Check if task should pause (called by task function)"""
        self._pause_event.wait()
        return False
        
    def _should_cancel(self) -> bool:
        """Check if task should cancel (called by task function)"""
        return self._cancel_flag
        
    def _progress_callback(self, step: int, total_steps: int, message: str = ""):
        """
        Called by task function to report progress.
        
        Args:
            step: Current step number
            total_steps: Total number of steps
            message: Status message
        """
        elapsed = time.time() - self._start_time
        
        # Calculate estimated remaining time
        if step > 0 and total_steps > 0:
            rate = elapsed / step
            estimated_remaining = rate * (total_steps - step)
        else:
            estimated_remaining = 0
            
        percent = (step / total_steps * 100) if total_steps > 0 else 0
        
        self._progress = ProgressInfo(
            step=step,
            total_steps=total_steps,
            percent=percent,
            message=message,
            elapsed_time=elapsed,
            estimated_remaining=estimated_remaining
        )
        
        self._events.put(("progress", self._progress))
            
    def _run_task(self, *args, **kwargs):
        """Execute the task function"""
        try:
            result = self.task_func(
                *args,
                progress_callback=self._progress_callback,
                should_pause=self._should_pause,
                should_cancel=self._should_cancel,
                **kwargs
            )
            
            if self._cancel_flag:
                self._state = TaskState.CANCELLED
            else:
                self._state = TaskState.COMPLETED
                self._events.put(("complete", result))
                    
        except Exception as e:
            self._state = TaskState.FAILED
            self._events.put(("error", e))


def run_full_pipeline_with_progress(
    fasta_files, output_dir, min_cds_len=201, tree_mode="both", verbose=False,
    progress_callback=None, should_pause=None, should_cancel=None
):
    """
    Run the full CDST pipeline with progress reporting.
    
    This is a wrapper around core.run_full_pipeline that adds progress callbacks.
    """
    import os
    import json
    from cdst import core
    
    os.makedirs(output_dir, exist_ok=True)
    
    total_files = len(fasta_files)
    
    # Step 1: Generate MD5 hashes (40% of progress)
    if progress_callback:
        progress_callback(0, 5, "正在生成 MD5 哈希...")
    
    md5_dict = {}
    for i, fasta_file in enumerate(fasta_files):
        if should_cancel and should_cancel():
            return None
            
        if should_pause:
            should_pause()
            
        md5_dict[fasta_file] = core.generate_md5_for_fasta(
            fasta_file, min_cds_len=min_cds_len, verbose=verbose
        )
        
        if progress_callback:
            step_pct = (i + 1) / total_files
            progress_callback(
                int(step_pct * 2), 5,
                f"正在处理文件 {i+1}/{total_files}: {os.path.basename(fasta_file)}"
            )
    
    json_output_path = os.path.join(output_dir, "md5_hashes.json")
    with open(json_output_path, "w") as f:
        json.dump(md5_dict, f, indent=4)
    
    # Step 2: Generate comparison matrix (60% of progress)
    if progress_callback:
        progress_callback(2, 5, "正在计算比较矩阵...")
    
    comparison_matrix = core.generate_comparison_matrix(md5_dict, verbose=verbose)
    comp_path = os.path.join(output_dir, "comparison_matrix.csv")
    comparison_matrix.to_csv(comp_path)
    
    # Step 3: Calculate difference matrix (80% of progress)
    if progress_callback:
        progress_callback(3, 5, "正在计算差异矩阵...")
    
    diff_matrix = core.calculate_difference_matrix(comparison_matrix)
    diff_path = os.path.join(output_dir, "difference_matrix.csv")
    diff_matrix.to_csv(diff_path)
    
    # Step 4: Generate MST
    if tree_mode in ("mst", "both"):
        if progress_callback:
            progress_callback(4, 5, "正在生成最小生成树...")
            
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
    
    # Step 5: Generate HC tree
    if tree_mode in ("hc", "both"):
        if progress_callback:
            progress_callback(4, 5, "正在生成层次聚类树...")
            
        hc_tree = core.generate_hc_tree(diff_matrix)
        leaf_names = list(diff_matrix.index)
        newick_str = core.tree_to_newick(hc_tree, "", hc_tree.dist, leaf_names)
        hc_newick = os.path.join(output_dir, "hc.newick")
        with open(hc_newick, "w") as f:
            f.write(newick_str)
    
    # Done
    if progress_callback:
        progress_callback(5, 5, "分析完成！")
    
    return output_dir
