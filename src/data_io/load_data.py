import os
from src.constants import DATA_DIR, SNAP_FOLDERS
from src.structures.graph import Graph

# Helper for loading a file
def load_snap_file(path):
    edges = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip commented lines
                continue
            parts = line.split()
            if len(parts) >= 2:  # Avoid non-data rows
                u, v = int(parts[0]), int(parts[1])
                edges.append((u, v))
    return edges




def load_all():
    """Load all SNAP datasets into memory."""
    datasets = {}
    for folder in SNAP_FOLDERS:
        folder_path = os.path.join(DATA_DIR, folder)
        datasets[folder] = {}

        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                datasets[folder][filename] = load_snap_file(filepath)
    return datasets

def load(folder, filename):
    """Load a single SNAP dataset by folder and filename."""
    folder_path = os.path.join(DATA_DIR, folder)
    filepath = os.path.join(folder_path, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"No such dataset: {folder}/{filename}")
    return load_snap_file(filepath)

def load_lazy():
    """
    Return (list_of_datasets, loader_map).
    list_of_datasets: [(folder, filename), ...]
    loader_map: {(folder, filename): function_that_loads_it}
    """
    datasets = []
    loader_map = {}

    for folder in SNAP_FOLDERS:
        folder_path = os.path.join(DATA_DIR, folder)
        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                key = (folder, filename)
                datasets.append(key)
                loader_map[key] = lambda fp=filepath: load_snap_file(fp)

    return datasets, loader_map


def load_metis_graph(path) -> Graph:
    """
    Reads a METIS .metis graph file and returns a Graph object.
    Labels are preserved exactly as they appear in the file, until passed into Graph object.

    METIS format:
        n m
        neighbors of node 1
        neighbors of node 2
        ...
    """
    edge_list = []
    nodes = set()

    with open(path, "r") as f:
        # Parse header: number of nodes, number of edges (undirected)
        first = f.readline().strip()
        if not first:
            raise ValueError(f"Empty METIS file: {path}")

        parts = first.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid METIS header in {path}: '{first}'")

        n = int(parts[0])   # number of nodes
        m = int(parts[1])   # number of edges (undirected)

        # METIS nodes are 1-indexed by definition
        # Lines following header correspond to node labels 1, 2, ..., n
        for u in range(1, n + 1):
            line = f.readline()
            if not line:
                raise ValueError(
                    f"METIS file ended early: expected adjacency list for node {u}"
                )

            line = line.strip()
            if not line:     # empty adjacency list is allowed
                nodes.add(u)
                continue

            neighbors = line.split()

            for v_str in neighbors:
                v = int(v_str)

                # Maintain label set
                nodes.add(u)
                nodes.add(v)

                # Avoid self-loops
                if u == v:
                    continue

                # Avoid duplicate edges: only keep (min,max)
                a, b = (u, v) if u < v else (v, u)
                edge_list.append((a, b))

    # Deduplicate final edges
    edge_list = list(set(edge_list))

    # Sort for consistency
    edge_list.sort()
    nodes = sorted(nodes)

    return Graph(edge_list=edge_list, nodes=nodes, name=path)
