import os
from src.constants import DATA_DIR, SNAP_FOLDERS

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
