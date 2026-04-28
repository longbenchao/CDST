"""
Results Viewer Tab - Visualize analysis results
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import tempfile

from ..utils.config import ConfigManager


def _ensure_matplotlib_config_dir():
    """Use an app-owned matplotlib cache directory when possible."""
    app_config_dir = os.path.join(os.path.expanduser("~"), ".cdst")
    config_dir = os.path.join(app_config_dir, "matplotlib")
    cache_dir = os.path.join(app_config_dir, "cache")
    try:
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        test_path = os.path.join(config_dir, ".write_test")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        os.environ.setdefault("MPLCONFIGDIR", config_dir)
        os.environ.setdefault("XDG_CACHE_HOME", cache_dir)
    except Exception:
        tmp_cache_dir = os.path.join(tempfile.gettempdir(), "cdst-cache")
        os.makedirs(os.path.join(tmp_cache_dir, "matplotlib"), exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", os.path.join(tmp_cache_dir, "matplotlib"))
        os.environ.setdefault("XDG_CACHE_HOME", tmp_cache_dir)


class ResultsViewerTab:
    """Results viewer tab for visualizing analysis results."""
    
    def __init__(self, parent, config: ConfigManager):
        self.parent = parent
        self.config = config
        self.result_dir = ""
        self.current_figure = None
        self.current_canvas = None
        self._resize_after_id = None
        self._last_plot = None
        self.current_clusters = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for results viewer"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        # === Result Directory Selection ===
        self.select_frame = ctk.CTkFrame(self.main_frame)
        self.select_frame.pack(fill="x", padx=6, pady=(6, 4))
        
        ctk.CTkLabel(
            self.select_frame,
            text="📁 结果目录:",
            width=100,
            anchor="w"
        ).pack(side="left", padx=(10, 5), pady=8)
        
        self.result_entry = ctk.CTkEntry(
            self.select_frame,
            placeholder_text="选择包含结果的目录...",
            width=400
        )
        self.result_entry.pack(side="left", padx=5, pady=8, fill="x", expand=True)
        
        ctk.CTkButton(
            self.select_frame,
            text="浏览",
            command=self._select_result_dir,
            width=80
        ).pack(side="left", padx=(5, 10), pady=8)
        
        ctk.CTkButton(
            self.select_frame,
            text="加载结果",
            command=self._load_results,
            width=100
        ).pack(side="left", padx=5, pady=8)
        
        # === Available Results ===
        self.avail_frame = ctk.CTkFrame(self.main_frame)
        self.avail_frame.pack(fill="x", padx=6, pady=(0, 4))
        
        ctk.CTkLabel(
            self.avail_frame,
            text="可用结果文件:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        
        self.result_list = ctk.CTkFrame(self.avail_frame, fg_color="transparent")
        self.result_list.pack(fill="x", padx=10, pady=(0, 8))
        
        # Placeholder labels
        self.result_labels = {}
        result_types = ["md5_hashes.json", "combined_md5_hashes.json",
                           "comparison_matrix.csv", "combined_comparison_matrix.csv",
                           "difference_matrix.csv", "combined_difference_matrix.csv",
                           "mst.csv", "combined_mst.csv", "mst.newick", "combined_mst.newick",
                           "hc.newick"]
        for i, result_type in enumerate(result_types):
            label = ctk.CTkLabel(
                self.result_list,
                text=f"○ {result_type}",
                text_color="gray",
                anchor="w"
            )
            label.grid(row=i // 4, column=i % 4, sticky="w", padx=(0, 18), pady=1)
            self.result_labels[result_type] = label
            
        # === Visualization Buttons ===
        self.viz_btn_frame = ctk.CTkFrame(self.main_frame)
        self.viz_btn_frame.pack(fill="x", padx=6, pady=(0, 4))
        
        ctk.CTkButton(
            self.viz_btn_frame,
            text="HC树分析",
            command=self._show_hc_tree,
            width=150
        ).pack(side="left", padx=6, pady=8)

        ctk.CTkLabel(
            self.viz_btn_frame,
            text="阈值:",
            anchor="e",
        ).pack(side="left", padx=(10, 2), pady=8)

        self.hc_threshold_entry = ctk.CTkEntry(
            self.viz_btn_frame,
            width=80,
            placeholder_text="auto"
        )
        self.hc_threshold_entry.pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            self.viz_btn_frame,
            text="应用阈值",
            command=self._show_hc_tree,
            width=90
        ).pack(side="left", padx=4, pady=8)
        
        ctk.CTkButton(
            self.viz_btn_frame,
            text="导出分群",
            command=self._export_current_clusters,
            width=90
        ).pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            self.viz_btn_frame,
            text="聚类矩阵图",
            command=self._show_heatmap,
            width=150
        ).pack(side="left", padx=6, pady=8)
        
        ctk.CTkButton(
            self.viz_btn_frame,
            text="MST网络图",
            command=self._show_mst_tree,
            width=150
        ).pack(side="left", padx=6, pady=8)
        
        ctk.CTkButton(
            self.viz_btn_frame,
            text="📋 统计信息",
            command=self._show_statistics,
            width=150
        ).pack(side="left", padx=6, pady=8)

        ctk.CTkButton(
            self.viz_btn_frame,
            text="放大查看",
            command=self._open_large_figure,
            width=100
        ).pack(side="left", padx=6, pady=8)

        ctk.CTkButton(
            self.viz_btn_frame,
            text="导出图片",
            command=self._export_current_figure,
            width=100
        ).pack(side="left", padx=6, pady=8)
        
        # === Visualization Area ===
        self.viz_frame = ctk.CTkFrame(self.main_frame)
        self.viz_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        
        ctk.CTkLabel(
            self.viz_frame,
            text="可视化区域",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        
        self.viz_display = ctk.CTkTextbox(self.viz_frame)
        self.viz_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.viz_display.insert("1.0", "请选择结果目录并加载结果...")
        
    def _select_result_dir(self):
        """Select result directory"""
        directory = filedialog.askdirectory(title="选择结果目录")
        if directory:
            self.result_dir = directory
            self.result_entry.delete(0, 'end')
            self.result_entry.insert(0, directory)
            
    def _load_results(self):
        """Load results from directory"""
        if not self.result_dir or not os.path.exists(self.result_dir):
            messagebox.showerror("错误", "请选择有效的结果目录！")
            return
            
        # Check for available result files
        available_files = []
        for result_type in self.result_labels.keys():
            file_path = os.path.join(self.result_dir, result_type)
            if os.path.exists(file_path):
                available_files.append(result_type)
                self.result_labels[result_type].configure(
                    text=f"✓ {result_type}",
                    text_color="green"
                )
            else:
                self.result_labels[result_type].configure(
                    text=f"○ {result_type}",
                    text_color="gray"
                )
                
        if available_files:
            self.viz_display.delete("1.0", "end")
            self.viz_display.insert("1.0", f"已加载结果目录: {self.result_dir}\n\n")
            self.viz_display.insert("end", f"找到 {len(available_files)} 个结果文件:\n")
            for f in available_files:
                self.viz_display.insert("end", f"  • {f}\n")
            if any(name in available_files for name in ("difference_matrix.csv", "combined_difference_matrix.csv")):
                self._set_auto_threshold()
                self._show_hc_tree(show_summary=False)
        else:
            messagebox.showinfo("提示", "未找到任何结果文件")

    def _clear_visualization(self):
        """Clear the visualization area."""
        if self._resize_after_id is not None:
            self.viz_frame.after_cancel(self._resize_after_id)
            self._resize_after_id = None
        if self.current_canvas is not None:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None
        self.current_figure = None

        if self.viz_display.winfo_exists():
            self.viz_display.pack_forget()

    def _show_text(self, text: str):
        """Show text in the visualization area."""
        self._clear_visualization()
        self.viz_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.viz_display.delete("1.0", "end")
        self.viz_display.insert("1.0", text)
        self._last_plot = None
        self.current_clusters = None

    def _show_figure(self, figure, target_frame=None):
        """Embed a matplotlib figure in the visualization area."""
        target_frame = target_frame or self.viz_frame
        if target_frame is self.viz_frame:
            self._clear_visualization()
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception as e:
            self._show_text(f"无法加载 matplotlib Tk 后端:\n{e}")
            return

        canvas = FigureCanvasTkAgg(figure, master=target_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if target_frame is self.viz_frame:
            self.current_figure = figure
            self.current_canvas = canvas
            canvas_widget.bind("<Configure>", self._resize_current_figure)
            self.viz_frame.after_idle(lambda: self._fit_figure_to_canvas(canvas_widget))
        else:
            canvas_widget.bind(
                "<Configure>",
                lambda event: self._fit_specific_figure(figure, canvas, event.widget, min_width=1200, min_height=760),
            )
            target_frame.after_idle(lambda: self._fit_specific_figure(figure, canvas, canvas_widget, min_width=1200, min_height=760))

    def _resize_current_figure(self, event):
        """Resize the matplotlib figure to fill the available canvas area."""
        if self.current_figure is None or self.current_canvas is None:
            return

        if self._resize_after_id is not None:
            self.viz_frame.after_cancel(self._resize_after_id)
        self._resize_after_id = self.viz_frame.after(
            120,
            lambda: self._fit_figure_to_canvas(event.widget),
        )

    def _fit_figure_to_canvas(self, canvas_widget):
        """Fit the figure size to the Tk canvas dimensions."""
        if self.current_figure is None or self.current_canvas is None:
            return

        width = max(canvas_widget.winfo_width(), 700)
        height = max(canvas_widget.winfo_height(), 480)
        self._fit_specific_figure(self.current_figure, self.current_canvas, canvas_widget, width, height)
        self._resize_after_id = None

    def _fit_specific_figure(self, figure, canvas, canvas_widget, min_width=700, min_height=480):
        """Fit a specific matplotlib figure/canvas pair to a widget."""
        width = max(canvas_widget.winfo_width(), min_width)
        height = max(canvas_widget.winfo_height(), min_height)
        dpi = figure.get_dpi()
        figure.set_size_inches(width / dpi, height / dpi, forward=True)
        if not figure.get_constrained_layout():
            figure.tight_layout()
        canvas.draw_idle()

    def _create_heatmap_figure(self, large=False):
        """Create a clustered distance matrix with a vertical HC tree."""
        matrix_file, df = self._load_difference_matrix()
        _ensure_matplotlib_config_dir()
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        from scipy.cluster.hierarchy import dendrogram, linkage
        from scipy.spatial.distance import squareform

        labels = [self._sample_label(label) for label in df.index]
        n_samples = len(labels)
        fig_width = max(14 if large else 11, min(34 if large else 24, n_samples * (0.42 if large else 0.32)))
        fig_height = max(10 if large else 7, min(36 if large else 24, n_samples * (0.24 if large else 0.18)))
        fig = plt.figure(figsize=(fig_width, fig_height), constrained_layout=True)

        if n_samples > 1:
            z = linkage(squareform(df), method="average")
            grid = GridSpec(1, 2, width_ratios=[1.1, 3.2], wspace=0.02, figure=fig)
            tree_ax = fig.add_subplot(grid[0, 0])
            heat_ax = fig.add_subplot(grid[0, 1])

            dendro = dendrogram(
                z,
                labels=labels,
                orientation="right",
                leaf_font_size=8 if large else 6,
                color_threshold=None,
                ax=tree_ax,
            )
            ordered = dendro["leaves"]
            ordered_df = df.iloc[ordered, ordered]
            ordered_labels = [labels[i] for i in ordered]
            tree_ax.set_xlabel("Distance")
            tree_ax.tick_params(axis="y", labelsize=8 if large else 6)

            im = heat_ax.imshow(ordered_df.values, cmap=self.config.get("color_scheme", "viridis"), aspect="auto")
            heat_ax.set_title(f"Clustered Distance Matrix - {os.path.basename(matrix_file)}")
            heat_ax.set_xticks(range(n_samples))
            heat_ax.set_yticks(range(n_samples))
            heat_ax.set_xticklabels(ordered_labels, rotation=90, fontsize=8 if large else 6)
            heat_ax.set_yticklabels(ordered_labels, fontsize=8 if large else 6)
            fig.colorbar(im, ax=heat_ax, fraction=0.046, pad=0.02, label="Distance")
        else:
            ax = fig.add_subplot(111)
            im = ax.imshow(df.values, cmap=self.config.get("color_scheme", "viridis"))
            ax.set_title(f"Distance Matrix - {os.path.basename(matrix_file)}")
            ax.set_xticks([0])
            ax.set_yticks([0])
            ax.set_xticklabels(labels, rotation=90)
            ax.set_yticklabels(labels)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Distance")

        return fig

    def _create_mst_figure(self, large=False):
        """Create a GrapeTree-style MST network figure."""
        mst_file = None
        for name in ["mst.csv", "combined_mst.csv"]:
            path = os.path.join(self.result_dir, name)
            if os.path.exists(path):
                mst_file = path
                break
        if mst_file is None:
            raise FileNotFoundError("未找到 MST CSV 文件！")

        _ensure_matplotlib_config_dir()
        import pandas as pd
        import networkx as nx
        import matplotlib.pyplot as plt

        df = pd.read_csv(mst_file)
        graph = nx.Graph()
        for _, row in df.iterrows():
            graph.add_edge(row["Node1"], row["Node2"], weight=float(row["Distance"]))

        fig, ax = plt.subplots(figsize=(18, 14) if large else (13, 10))
        pos = self._grapetree_like_layout(graph)
        labels = {node: self._sample_label(node) for node in graph.nodes}
        edge_weights = [graph[u][v].get("weight", 0.0) for u, v in graph.edges]
        max_weight = max(edge_weights) if edge_weights else 1.0
        widths = [max(0.8, 3.2 - (w / max_weight * 2.2 if max_weight else 0)) for w in edge_weights]
        node_sizes = [380 + graph.degree(node) * (90 if large else 60) for node in graph.nodes]

        nx.draw_networkx_edges(graph, pos, width=widths, edge_color="#6e7781", alpha=0.75, ax=ax)
        nx.draw_networkx_nodes(
            graph,
            pos,
            node_size=node_sizes,
            node_color="#f2b84b",
            edgecolors="#2f3437",
            linewidths=0.8,
            ax=ax,
        )
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8 if large else 6, ax=ax)
        if len(graph.edges) <= (80 if large else 35):
            edge_labels = {
                (u, v): f"{graph[u][v].get('weight', 0):.3g}"
                for u, v in graph.edges
                if graph[u][v].get("weight", 0) > 0
            }
            nx.draw_networkx_edge_labels(edge_labels=edge_labels, G=graph, pos=pos, font_size=6 if large else 5, ax=ax)
        ax.set_title(f"MST Network (GrapeTree-style) - {os.path.basename(mst_file)}")
        ax.axis("off")
        fig.tight_layout()
        return fig

    def _create_hc_figure(self, large=False, threshold=None):
        """Create a vertical hierarchical clustering dendrogram figure."""
        _, df = self._load_difference_matrix()
        _ensure_matplotlib_config_dir()
        import matplotlib.pyplot as plt
        from scipy.cluster.hierarchy import dendrogram, linkage
        from scipy.spatial.distance import squareform

        labels = [self._sample_label(label) for label in df.index]
        condensed = squareform(df)
        z = linkage(condensed, method="average")
        fig_width = 16 if large else 12
        fig_height = max(10 if large else 7, min(42 if large else 28, len(labels) * (0.28 if large else 0.22)))
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        color_threshold = threshold if threshold is not None else None
        dendrogram(
            z,
            labels=labels,
            orientation="right",
            leaf_font_size=8 if large else 6,
            color_threshold=color_threshold,
            ax=ax,
        )
        if threshold is not None:
            ax.axvline(threshold, color="#d62728", linestyle="--", linewidth=1.4)
            ax.text(
                threshold,
                1.01,
                f"threshold={threshold:.4f}",
                color="#d62728",
                transform=ax.get_xaxis_transform(),
                ha="left",
                va="bottom",
                fontsize=8 if large else 7,
            )
        ax.set_title("Hierarchical Clustering Tree")
        ax.set_xlabel("Distance")
        ax.tick_params(axis="y", labelsize=8 if large else 6)
        fig.tight_layout()
        return fig

    def _get_threshold(self, df=None):
        """Read or infer the HC cut threshold."""
        value = self.hc_threshold_entry.get().strip()
        if value:
            return float(value)

        if df is None:
            _, df = self._load_difference_matrix()
        return self._auto_threshold_from_matrix(df)

    def _auto_threshold_from_matrix(self, df):
        """Infer a practical default threshold from the pairwise distance distribution."""
        import numpy as np

        values = df.values
        mask = ~np.eye(values.shape[0], dtype=bool)
        pairwise = values[mask]
        pairwise = pairwise[pairwise > 0]
        if len(pairwise) == 0:
            return 0.0
        return float(np.quantile(pairwise, 0.10))

    def _set_auto_threshold(self):
        """Fill the HC threshold entry with an inferred default value."""
        try:
            _, df = self._load_difference_matrix()
            threshold = self._auto_threshold_from_matrix(df)
        except Exception:
            return

        self.hc_threshold_entry.delete(0, "end")
        self.hc_threshold_entry.insert(0, f"{threshold:.4f}")

    def _cluster_samples(self, threshold):
        """Cut the HC tree at a threshold and build cluster assignments and summaries."""
        import pandas as pd
        from scipy.cluster.hierarchy import fcluster, linkage
        from scipy.spatial.distance import squareform

        _, df = self._load_difference_matrix()
        labels = [self._sample_label(label) for label in df.index]
        if len(labels) == 1:
            assignments = pd.DataFrame({"Sample": labels, "Cluster": [1]})
            summary = pd.DataFrame({
                "Cluster": [1],
                "Samples": [1],
                "MeanDistance": [0.0],
                "MaxDistance": [0.0],
                "Members": [labels[0]],
            })
            return assignments, summary

        z = linkage(squareform(df), method="average")
        raw_clusters = fcluster(z, t=threshold, criterion="distance")
        unique_clusters = {cluster: i + 1 for i, cluster in enumerate(sorted(set(raw_clusters)))}
        clusters = [unique_clusters[cluster] for cluster in raw_clusters]
        assignments = pd.DataFrame({"Sample": labels, "Cluster": clusters})

        summary_rows = []
        for cluster_id, group in assignments.groupby("Cluster"):
            indices = group.index.tolist()
            sub = df.iloc[indices, indices]
            if len(indices) > 1:
                values = sub.values
                pair_values = values[~pd.DataFrame(
                    [[i == j for j in range(values.shape[1])] for i in range(values.shape[0])]
                ).values]
                mean_distance = float(pair_values.mean()) if len(pair_values) else 0.0
                max_distance = float(pair_values.max()) if len(pair_values) else 0.0
            else:
                mean_distance = 0.0
                max_distance = 0.0
            summary_rows.append({
                "Cluster": int(cluster_id),
                "Samples": len(indices),
                "MeanDistance": mean_distance,
                "MaxDistance": max_distance,
                "Members": ", ".join(group["Sample"].tolist()),
            })

        summary = pd.DataFrame(summary_rows).sort_values(["Samples", "Cluster"], ascending=[False, True])
        return assignments, summary

    def _build_hc_analysis_text(self, threshold, assignments, summary):
        """Build a concise textual HC cluster summary."""
        lines = [
            "HC 聚类分析",
            "",
            f"距离阈值: {threshold:.4f}",
            f"分群数量: {len(summary)}",
            f"样本数量: {len(assignments)}",
            "",
            "分群摘要:",
            "Cluster\tSamples\tMeanDistance\tMaxDistance\tMembers",
        ]
        for _, row in summary.iterrows():
            lines.append(
                f"{int(row['Cluster'])}\t{int(row['Samples'])}\t"
                f"{row['MeanDistance']:.4f}\t{row['MaxDistance']:.4f}\t{row['Members']}"
            )
        return "\n".join(lines)

    def _sample_label(self, value):
        """Format sample names for tree labels."""
        label = os.path.basename(str(value))
        for suffix in (".ffn", ".fasta", ".fa", ".fna"):
            if label.lower().endswith(suffix):
                return label[:-len(suffix)]
        return label

    def _grapetree_like_layout(self, graph):
        """Build a deterministic radial tree layout similar to GrapeTree views."""
        import math

        if not graph.nodes:
            return {}
        if len(graph.nodes) == 1:
            node = next(iter(graph.nodes))
            return {node: (0.0, 0.0)}

        root = max(graph.nodes, key=lambda node: (graph.degree(node), str(node)))
        adjacency = {node: sorted(graph.neighbors(node), key=str) for node in graph.nodes}
        parent = {root: None}
        children = {node: [] for node in graph.nodes}
        stack = [root]
        order = []
        while stack:
            node = stack.pop()
            order.append(node)
            for neighbor in reversed(adjacency[node]):
                if neighbor in parent:
                    continue
                parent[neighbor] = node
                children[node].append(neighbor)
                stack.append(neighbor)

        subtree_size = {}
        for node in reversed(order):
            subtree_size[node] = max(1, sum(subtree_size[child] for child in children[node]))

        max_weight = max((data.get("weight", 0.0) for _, _, data in graph.edges(data=True)), default=1.0) or 1.0
        pos = {root: (0.0, 0.0)}

        def place(node, start_angle, end_angle, radius):
            kids = children[node]
            if not kids:
                return
            total = sum(subtree_size[child] for child in kids)
            cursor = start_angle
            for child in kids:
                span = (end_angle - start_angle) * (subtree_size[child] / total)
                angle = cursor + span / 2
                weight = graph[node][child].get("weight", 0.0)
                step = 1.0 + (weight / max_weight) * 1.6
                child_radius = radius + step
                pos[child] = (child_radius * math.cos(angle), child_radius * math.sin(angle))
                place(child, cursor, cursor + span, child_radius)
                cursor += span

        place(root, 0.0, 2 * math.pi, 0.0)
        return pos

    def _load_difference_matrix(self):
        """Load the best available difference matrix from result_dir."""
        candidates = ["difference_matrix.csv", "combined_difference_matrix.csv"]
        for name in candidates:
            path = os.path.join(self.result_dir, name)
            if os.path.exists(path):
                import pandas as pd
                import numpy as np

                df = pd.read_csv(path, index_col=0)
                df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
                shared_labels = [label for label in df.index if label in df.columns]
                if not shared_labels:
                    raise ValueError("差异矩阵的行名和列名不匹配，无法进行 HC 聚类。")
                df = df.loc[shared_labels, shared_labels]
                values = np.minimum(df.values, df.values.T)
                np.fill_diagonal(values, 0.0)
                symmetric_df = pd.DataFrame(values, index=shared_labels, columns=shared_labels)
                return path, symmetric_df
        raise FileNotFoundError("未找到差异矩阵文件！")
            
    def _show_heatmap(self):
        """Show distance matrix heatmap"""
        try:
            fig = self._create_heatmap_figure()
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return

        self._last_plot = "heatmap"
        self._show_figure(fig)
        
    def _show_mst_tree(self):
        """Show MST tree"""
        try:
            fig = self._create_mst_figure()
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return

        self._last_plot = "mst"
        self._show_figure(fig)
        
    def _show_hc_tree(self, show_summary=True):
        """Show HC tree"""
        try:
            _, df = self._load_difference_matrix()
            threshold = self._get_threshold(df)
            assignments, summary = self._cluster_samples(threshold)
            fig = self._create_hc_figure(threshold=threshold)
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return

        self.current_clusters = assignments
        self._last_plot = "hc"
        self._show_figure(fig)
        if show_summary:
            self._show_hc_summary_window(threshold, assignments, summary)

    def _show_hc_summary_window(self, threshold, assignments, summary):
        """Show HC cluster summary in a compact side window."""
        text = self._build_hc_analysis_text(threshold, assignments, summary)
        window = ctk.CTkToplevel(self.parent)
        window.title("HC 分群摘要")
        window.geometry("760x520")
        window.minsize(620, 420)

        toolbar = ctk.CTkFrame(window)
        toolbar.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(
            toolbar,
            text=f"阈值 {threshold:.4f} | {len(summary)} 个分群",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=8, pady=6)
        ctk.CTkButton(
            toolbar,
            text="导出分群",
            width=100,
            command=self._export_current_clusters,
        ).pack(side="right", padx=8, pady=6)

        textbox = ctk.CTkTextbox(window)
        textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        textbox.insert("1.0", text)
        
    def _show_statistics(self):
        """Show statistics"""
        lines = ["统计分析", ""]
        
        # Check for available files
        stats = {}
        
        # MD5 hashes
        json_file = os.path.join(self.result_dir, "md5_hashes.json")
        if not os.path.exists(json_file):
            json_file = os.path.join(self.result_dir, "combined_md5_hashes.json")
        if os.path.exists(json_file):
            import json
            with open(json_file, 'r') as f:
                md5_dict = json.load(f)
            total_hashes = sum(len(v) for v in md5_dict.values())
            unique_hashes = len(set(h for v in md5_dict.values() for h in v))
            stats['样本数'] = len(md5_dict)
            stats['总哈希数'] = total_hashes
            stats['唯一哈希数'] = unique_hashes
            
        # Matrix
        try:
            import pandas as pd
            _, df = self._load_difference_matrix()
            stats['矩阵维度'] = f"{df.shape[0]} x {df.shape[1]}"
            mask = ~pd.DataFrame(
                [[i == j for j in range(df.shape[1])] for i in range(df.shape[0])]
            ).values
            pairwise = df.values[mask]
            stats['平均距离'] = f"{pairwise.mean():.4f}" if len(pairwise) else "0.0000"
            stats['最小距离'] = f"{pairwise.min():.4f}" if len(pairwise) else "0.0000"
            stats['最大距离'] = f"{pairwise.max():.4f}" if len(pairwise) else "0.0000"
        except Exception:
            pass
            
        if stats:
            lines.append("统计信息:")
            lines.append("-" * 40)
            for key, value in stats.items():
                lines.append(f"{key:15s}: {value}")
        else:
            lines.append("未找到可分析的结果文件。")
        self._show_text("\n".join(lines))

    def _open_large_figure(self):
        """Open the current visualization in a larger window."""
        if self._last_plot is None:
            messagebox.showinfo("提示", "请先生成热图、MST 或 HC 图。")
            return

        try:
            if self._last_plot == "heatmap":
                fig = self._create_heatmap_figure(large=True)
            elif self._last_plot == "mst":
                fig = self._create_mst_figure(large=True)
            elif self._last_plot == "hc":
                fig = self._create_hc_figure(large=True, threshold=self._get_threshold())
            else:
                messagebox.showinfo("提示", "当前图表不能放大查看。")
                return
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return

        window = ctk.CTkToplevel(self.parent)
        window.title("CDST 可视化放大查看")
        window.geometry("1600x1000")
        window.minsize(1200, 760)

        toolbar = ctk.CTkFrame(window)
        toolbar.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(toolbar, text="放大查看", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=8, pady=6)
        ctk.CTkButton(
            toolbar,
            text="导出图片",
            width=100,
            command=lambda: self._export_figure(fig),
        ).pack(side="right", padx=8, pady=6)

        figure_frame = ctk.CTkFrame(window)
        figure_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._show_figure(fig, target_frame=figure_frame)

    def _export_current_figure(self):
        """Export the currently displayed figure."""
        if self.current_figure is None:
            messagebox.showinfo("提示", "当前没有可导出的图片。")
            return
        self._export_figure(self.current_figure)

    def _export_current_clusters(self):
        """Export current HC cluster assignments."""
        if self.current_clusters is None:
            try:
                threshold = self._get_threshold()
                assignments, _ = self._cluster_samples(threshold)
                self.current_clusters = assignments
            except Exception as e:
                messagebox.showerror("错误", str(e))
                return

        output_path = filedialog.asksaveasfilename(
            title="导出 HC 分群表",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        )
        if not output_path:
            return

        self.current_clusters.to_csv(output_path, index=False)
        messagebox.showinfo("完成", f"分群表已导出:\n{output_path}")

    def _export_figure(self, figure):
        """Export a matplotlib figure."""
        image_format = self.config.get("image_format", "png")
        output_path = filedialog.asksaveasfilename(
            title="导出图片",
            defaultextension=f".{image_format}",
            filetypes=[
                ("PNG 图片", "*.png"),
                ("PDF 文件", "*.pdf"),
                ("SVG 文件", "*.svg"),
                ("所有文件", "*.*"),
            ],
        )
        if not output_path:
            return

        figure.savefig(output_path, dpi=self.config.get("image_dpi", 300), bbox_inches="tight")
        messagebox.showinfo("完成", f"图片已导出:\n{output_path}")
