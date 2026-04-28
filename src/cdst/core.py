"""
Core functions for CDST (CoDing Sequence Typer).
Implements MD5-based hashing of CDS sequences, distance matrix generation,
minimum spanning tree (MST) construction, hierarchical clustering (HC) trees,
and comparison utilities.
"""

import hashlib
import json
import os
from typing import Dict, List, Tuple

import pandas as pd
import networkx as nx
from Bio import SeqIO
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform

# src/cdst/core.py  (append at the end)

def run_full_pipeline(fasta_files, output_dir, min_cds_len=201, tree_mode="both", verbose=False):
    """
    Run the full CDST pipeline:
    1. Generate MD5 hashes from FASTA files
    2. Create comparison and difference matrices
    3. Optionally generate MST and/or HC trees

    Parameters
    ----------
    fasta_files : list of str
        List of input CDS FASTA files (.ffn)
    output_dir : str
        Directory to write results
    min_cds_len : int
        Minimum CDS length (default=201)
    tree_mode : str
        One of {"mst", "hc", "both"}
    verbose : bool
        Verbose logging
    """
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: generate md5
    md5_dict = {}
    for fasta_file in fasta_files:
        md5_dict[fasta_file] = generate_md5_for_fasta(
            fasta_file, min_cds_len=min_cds_len, verbose=verbose
        )
    json_output_path = os.path.join(output_dir, "md5_hashes.json")
    with open(json_output_path, "w") as f:
        json.dump(md5_dict, f, indent=4)
    print(f"[cdst] MD5 hashes written to {json_output_path}")

    # Step 2: comparison + difference matrices
    comparison_matrix = generate_comparison_matrix(md5_dict, verbose=verbose)
    comp_path = os.path.join(output_dir, "comparison_matrix.csv")
    comparison_matrix.to_csv(comp_path)
    print(f"[cdst] Comparison matrix written to {comp_path}")

    diff_matrix = calculate_difference_matrix(comparison_matrix)
    diff_path = os.path.join(output_dir, "difference_matrix.csv")
    diff_matrix.to_csv(diff_path)
    print(f"[cdst] Difference matrix written to {diff_path}")

    # Step 3: MST
    if tree_mode in ("mst", "both"):
        edge_list = generate_edge_list(diff_matrix)
        mst_edges = generate_mst(edge_list)
        mst_csv = os.path.join(output_dir, "mst.csv")
        with open(mst_csv, "w") as f:
            f.write("Node1,Node2,Distance\n")
            for u, v, data in mst_edges:
                f.write(f"{u},{v},{data['weight']}\n")
        print(f"[cdst] MST edges written to {mst_csv}")
        newick_str = mst_to_newick(mst_edges, list(diff_matrix.index))
        mst_newick = os.path.join(output_dir, "mst.newick")
        with open(mst_newick, "w") as f:
            f.write(newick_str)
        print(f"[cdst] MST Newick tree written to {mst_newick}")

    # Step 4: HC
    if tree_mode in ("hc", "both"):
        hc_tree = generate_hc_tree(diff_matrix)
        leaf_names = list(diff_matrix.index)
        newick_str = tree_to_newick(hc_tree, "", hc_tree.dist, leaf_names)
        hc_newick = os.path.join(output_dir, "hc.newick")
        with open(hc_newick, "w") as f:
            f.write(newick_str)
        print(f"[cdst] HC Newick tree written to {hc_newick}")


def write_md5_database(md5_dict: Dict[str, List[str]], output_dir: str, filename: str = "md5_hashes.json") -> str:
    """Write an MD5 database JSON file and return its path."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        json.dump(md5_dict, f, indent=4)
    return output_path


def write_matrices(md5_dict: Dict[str, List[str]], output_dir: str, prefix: str = "", verbose: bool = False) -> Tuple[str, str]:
    """Generate comparison and difference matrices, write them, and return their paths."""
    os.makedirs(output_dir, exist_ok=True)
    comparison_matrix = generate_comparison_matrix(md5_dict, verbose=verbose)
    comparison_path = os.path.join(output_dir, f"{prefix}comparison_matrix.csv")
    comparison_matrix.to_csv(comparison_path)

    difference_matrix = calculate_difference_matrix(comparison_matrix)
    difference_path = os.path.join(output_dir, f"{prefix}difference_matrix.csv")
    difference_matrix.to_csv(difference_path)
    return comparison_path, difference_path


def write_tree_files(diff_matrix: pd.DataFrame, output_dir: str, tree_mode: str = "both", prefix: str = "") -> List[str]:
    """Generate MST and/or HC tree output files and return the paths written."""
    os.makedirs(output_dir, exist_ok=True)
    written = []

    if tree_mode in ("mst", "both"):
        edge_list = generate_edge_list(diff_matrix)
        edge_list_path = os.path.join(output_dir, f"{prefix}edge_list.csv")
        with open(edge_list_path, "w") as f:
            f.write("Sample1,Sample2,Distance\n")
            for sample1, sample2, distance in edge_list:
                f.write(f"{sample1},{sample2},{distance}\n")
        written.append(edge_list_path)

        mst_edges = generate_mst(edge_list)
        mst_csv = os.path.join(output_dir, f"{prefix}mst.csv")
        with open(mst_csv, "w") as f:
            f.write("Node1,Node2,Distance\n")
            for u, v, data in mst_edges:
                f.write(f"{u},{v},{data['weight']}\n")
        written.append(mst_csv)

        mst_newick = os.path.join(output_dir, f"{prefix}mst.newick")
        with open(mst_newick, "w") as f:
            f.write(mst_to_newick(mst_edges, list(diff_matrix.index)))
        written.append(mst_newick)

    if tree_mode in ("hc", "both"):
        hc_tree = generate_hc_tree(diff_matrix)
        leaf_names = list(diff_matrix.index)
        hc_newick = os.path.join(output_dir, f"{prefix}hc.newick")
        with open(hc_newick, "w") as f:
            f.write(tree_to_newick(hc_tree, "", hc_tree.dist, leaf_names))
        written.append(hc_newick)

    return written


def merge_matrices(existing_matrices: List[pd.DataFrame], md5_dict: Dict[str, List[str]], verbose: bool = False) -> pd.DataFrame:
    """
    Merge existing comparison matrices and fill missing pairs from the MD5 database.
    """
    samples = set(md5_dict.keys())
    for matrix in existing_matrices:
        samples.update(matrix.index)
        samples.update(matrix.columns)
    samples = sorted(samples)

    combined = pd.DataFrame(0, index=samples, columns=samples)
    for matrix in existing_matrices:
        for i in matrix.index:
            for j in matrix.columns:
                combined.loc[i, j] = matrix.loc[i, j]

    md5_sets = {sample: set(hashes) for sample, hashes in md5_dict.items()}
    for i, sample1 in enumerate(samples):
        set1 = md5_sets.get(sample1, set())
        for sample2 in samples[i:]:
            set2 = md5_sets.get(sample2, set())
            if sample1 == sample2:
                shared = len(set1)
            elif combined.loc[sample1, sample2] and combined.loc[sample2, sample1]:
                continue
            else:
                shared = len(set1 & set2)
            combined.loc[sample1, sample2] = shared
            combined.loc[sample2, sample1] = shared
            if verbose and sample1 != sample2:
                print(f"[cdst] Comparing {sample1} vs {sample2}")

    return combined


def join_databases(input_dirs: List[str], output_dir: str, generate_matrix: bool = False, generate_mst: bool = False, verbose: bool = False) -> Dict[str, str]:
    """
    Join multiple CDST database directories into one output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    combined_md5 = {}
    existing_matrices = []

    for input_dir in input_dirs:
        json_path = os.path.join(input_dir, "md5_hashes.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Missing md5_hashes.json in {input_dir}")
        with open(json_path, "r") as f:
            combined_md5.update(json.load(f))

        matrix_path = os.path.join(input_dir, "comparison_matrix.csv")
        if generate_matrix and os.path.exists(matrix_path):
            existing_matrices.append(pd.read_csv(matrix_path, index_col=0))

    outputs = {
        "md5": write_md5_database(combined_md5, output_dir, filename="combined_md5_hashes.json")
    }

    if generate_matrix:
        comparison_matrix = merge_matrices(existing_matrices, combined_md5, verbose=verbose)
        comparison_path = os.path.join(output_dir, "combined_comparison_matrix.csv")
        comparison_matrix.to_csv(comparison_path)
        outputs["comparison_matrix"] = comparison_path

        difference_matrix = calculate_difference_matrix(comparison_matrix)
        difference_path = os.path.join(output_dir, "combined_difference_matrix.csv")
        difference_matrix.to_csv(difference_path)
        outputs["difference_matrix"] = difference_path

        if generate_mst:
            tree_paths = write_tree_files(difference_matrix, output_dir, tree_mode="mst", prefix="combined_")
            outputs["tree_files"] = tree_paths

    return outputs


def compare_new_samples_with_existing(new_md5_dict: Dict[str, List[str]], existing_md5_dict: Dict[str, List[str]], verbose: bool = False):
    """
    Compare new samples against an existing MD5 database.
    """
    comparison_results_normalized = []
    comparison_results_unnormalized = []
    all_distances_normalized = []
    all_distances_unnormalized = []

    for new_sample, new_md5s in new_md5_dict.items():
        closest_norm = None
        closest_unnorm = None
        min_norm = float("inf")
        min_unnorm = float("inf")
        set_new = set(new_md5s)

        for existing_sample, existing_md5s in existing_md5_dict.items():
            set_exist = set(existing_md5s)
            common = set_new & set_exist

            d_a_b_norm = (len(set_new) - len(common)) / len(set_new) if set_new else 1.0
            d_b_a_norm = (len(set_exist) - len(common)) / len(set_exist) if set_exist else 1.0
            d_norm = min(d_a_b_norm, d_b_a_norm)

            d_a_b_unn = len(set_new) - len(common)
            d_b_a_unn = len(set_exist) - len(common)
            d_unn = min(d_a_b_unn, d_b_a_unn)

            all_distances_normalized.append((new_sample, existing_sample, d_norm))
            all_distances_unnormalized.append((new_sample, existing_sample, d_unn))

            if d_norm < min_norm:
                min_norm = d_norm
                closest_norm = existing_sample
            if d_unn < min_unnorm:
                min_unnorm = d_unn
                closest_unnorm = existing_sample

            if verbose:
                print(f"[cdst] {new_sample} vs {existing_sample}: norm={d_norm}, unnorm={d_unn}")

        comparison_results_normalized.append((new_sample, closest_norm, min_norm))
        comparison_results_unnormalized.append((new_sample, closest_unnorm, min_unnorm))

    return (
        comparison_results_normalized,
        comparison_results_unnormalized,
        all_distances_normalized,
        all_distances_unnormalized,
    )


def test_new_samples(fasta_files: List[str], existing_json: str, output_dir: str, min_cds_len: int = 201, verbose: bool = False) -> Dict[str, str]:
    """
    Compare new FASTA samples against an existing CDST JSON database and write CSV outputs.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(existing_json, "r") as f:
        existing_md5 = json.load(f)

    new_md5 = {
        fasta_file: generate_md5_for_fasta(fasta_file, min_cds_len=min_cds_len, verbose=verbose)
        for fasta_file in fasta_files
    }

    norm_results, unnorm_results, norm_distances, unnorm_distances = compare_new_samples_with_existing(
        new_md5, existing_md5, verbose=verbose
    )

    outputs = {
        "comparison_results_normalized": os.path.join(output_dir, "comparison_results_normalized.csv"),
        "comparison_results_unnormalized": os.path.join(output_dir, "comparison_results_unnormalized.csv"),
        "distances_normalized": os.path.join(output_dir, "distances_normalized.csv"),
        "distances_unnormalized": os.path.join(output_dir, "distances_unnormalized.csv"),
    }

    pd.DataFrame(norm_results, columns=["NewSample", "ClosestSample", "NormalizedDistance"]).to_csv(
        outputs["comparison_results_normalized"], index=False
    )
    pd.DataFrame(unnorm_results, columns=["NewSample", "ClosestSample", "UnnormalizedDistance"]).to_csv(
        outputs["comparison_results_unnormalized"], index=False
    )
    pd.DataFrame(norm_distances, columns=["Sample1", "Sample2", "NormalizedDistance"]).to_csv(
        outputs["distances_normalized"], index=False
    )
    pd.DataFrame(unnorm_distances, columns=["Sample1", "Sample2", "UnnormalizedDistance"]).to_csv(
        outputs["distances_unnormalized"], index=False
    )

    return outputs


def generate_md5_for_fasta(fasta_file: str, min_cds_len: int = 201, verbose: bool = False) -> List[str]:
    """
    Read CDS FASTA (e.g., Prodigal .ffn) and return a list of MD5 hashes
    after filtering for ambiguous bases and minimum length.
    """
    md5_list = []
    kept, skipped_len, skipped_ambig = 0, 0, 0
    if verbose:
        print(f"[cdst] Processing file: {fasta_file} (min_cds_len={min_cds_len})")
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq = str(record.seq)
        if any(ch not in "ATCGatcg" for ch in seq):
            skipped_ambig += 1
            continue
        if len(seq) < max(0, int(min_cds_len)):
            skipped_len += 1
            continue
        seq = seq.upper()
        md5_hash = hashlib.md5(seq.encode()).hexdigest()
        md5_list.append(md5_hash)
        kept += 1
    if verbose:
        print(f"[cdst] Kept: {kept}, Skipped (len): {skipped_len}, Skipped (ambiguous): {skipped_ambig}")
    return md5_list


def generate_comparison_matrix(md5_dict: Dict[str, List[str]], verbose: bool = False) -> pd.DataFrame:
    """
    Generate a pairwise comparison matrix of shared CDS counts.
    """
    files = list(md5_dict.keys())
    matrix = []
    total_comparisons = len(files) * len(files)
    comparison_count = 0
    for file1 in files:
        row = []
        set1 = set(md5_dict[file1])
        for file2 in files:
            common_md5s = set1 & set(md5_dict[file2])
            row.append(len(common_md5s))
            if verbose:
                comparison_count += 1
                if comparison_count % 100 == 0:
                    print(f"[cdst] Comparing {comparison_count}/{total_comparisons} ...", end="\r")
        matrix.append(row)
    if verbose:
        print("\n[cdst] Comparison completed.")
    return pd.DataFrame(matrix, index=files, columns=files)


def calculate_difference_matrix(comparison_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Compute relative differences and symmetrize the distance matrix.
    """
    diff_matrix = comparison_matrix.copy().astype(float)
    for idx, row in comparison_matrix.iterrows():
        self_comp = row[idx]
        if self_comp == 0:
            diff_matrix.loc[idx] = 1.0
            diff_matrix.loc[idx, idx] = 0.0
        else:
            diff_matrix.loc[idx] = (self_comp - row) / self_comp
    for i in range(len(diff_matrix)):
        for j in range(i + 1, len(diff_matrix)):
            m = min(diff_matrix.iloc[i, j], diff_matrix.iloc[j, i])
            diff_matrix.iloc[i, j] = diff_matrix.iloc[j, i] = m
    return diff_matrix


def generate_edge_list(diff_matrix: pd.DataFrame) -> List[Tuple[str, str, float]]:
    """
    Convert a distance matrix into an edge list.
    """
    edge_list = []
    samples = diff_matrix.index
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            s1 = samples[i]
            s2 = samples[j]
            d = diff_matrix.loc[s1, s2]
            edge_list.append((s1, s2, d))
    return edge_list


def generate_mst(edge_list: List[Tuple[str, str, float]]) -> List[Tuple[str, str, dict]]:
    """
    Build a minimum spanning tree (MST) from an edge list.
    """
    G = nx.Graph()
    G.add_weighted_edges_from(edge_list)
    mst = nx.minimum_spanning_tree(G)
    return list(mst.edges(data=True))


def mst_to_newick(mst_edges: List[Tuple[str, str, dict]], leaf_names: List[str]) -> str:
    """
    Convert MST edges into a Newick-formatted string.
    """
    connections = {name: [] for name in leaf_names}
    for u, v, data in mst_edges:
        connections[u].append((v, data['weight']))
        connections[v].append((u, data['weight']))

    def build_newick(node, parent=None):
        children = [n for n, _ in connections[node] if n != parent]
        if not children:
            return node
        subtrees = []
        for child in children:
            w = [w for n, w in connections[node] if n == child][0]
            subtrees.append(build_newick(child, node) + ":%f" % w)
        return "(" + ",".join(subtrees) + ")" + node

    root = leaf_names[0]
    return build_newick(root) + ";"


def generate_hc_tree(diff_matrix: pd.DataFrame):
    """
    Build a hierarchical clustering tree using average linkage.
    """
    sym = diff_matrix.copy()
    for i in range(len(sym)):
        for j in range(i + 1, len(sym)):
            m = min(sym.iloc[i, j], sym.iloc[j, i])
            sym.iloc[i, j] = sym.iloc[j, i] = m
    condensed = squareform(sym)
    Z = linkage(condensed, method='average')
    tree, _ = to_tree(Z, rd=True)
    return tree


def tree_to_newick(node, newick: str, parentdist: float, leaf_names: List[str]) -> str:
    """
    Recursively convert a hierarchical clustering tree into Newick format.
    """
    if node.is_leaf():
        return "%s:%.2f%s" % (leaf_names[node.id], parentdist - node.dist, newick)
    else:
        if len(newick) > 0:
            newick = "):%.2f%s" % (parentdist - node.dist, newick)
        else:
            newick = ");"
        newick = tree_to_newick(node.get_left(), newick, node.dist, leaf_names)
        newick = tree_to_newick(node.get_right(), ",%s" % newick, node.dist, leaf_names)
        newick = "(%s" % newick
        return newick
