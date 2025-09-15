from data_io.load_data import load_lazy
import networkx as nx
from graph import Graph

def get_graphs():
    '''
    Loads in the data lazily:
       datasets: list of (folder, filename)
            small_datasets: subset from "snap_datasets"
            large_datasets: subset from "new_snap_datasets"
       load_fn_map: dict {(folder, filename): fn that returns Graph}
    '''
    # Returns edge-list loaders
    datasets, load_fn_map = load_lazy()

    # Wrap each edge-list loader so it returns a Graph instead
    graph_load_fn_map = {}
    for key, edge_loader in load_fn_map.items():
        dir, name = key
        graph_load_fn_map[key] = lambda loader=edge_loader, n=name: Graph(loader(), name=n)

    small_datasets = [(d, n) for d, n in datasets if d == "snap_datasets"]
    large_datasets = [(d, n) for d, n in datasets if d == "new_snap_datasets"]
    test_datasets = [(d, n) for d, n in datasets if d == "test_datasets"]

    return datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map


def edges_to_graph(edge_list):
    return Graph(edge_list)


def path_to_graph(folder, filename):
    """Load a graph from a given dataset folder/filename pair."""
    datasets, _, _, load_fn_map = get_graphs()
    key = (folder, filename)

    if key not in load_fn_map:
        raise ValueError(f"No dataset found for {key}")
    
    return load_fn_map[key]()   # directly returns a Graph




