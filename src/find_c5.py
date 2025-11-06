from src.data_io.load_data import load_lazy
from src.data_io.process_data import get_graphs
from src.algorithms.degeneracy import get_degeneracy
from src.algorithms.slow_degeneracy import get_degeneracy_slow
from src.graph import Graph


from pprint import pprint
import time
import itertools
import networkx as nx
import matplotlib.pyplot as plt




C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [("snap_datasets", "ca-GrQc.txt"), ("snap_datasets","ca-HepTh.txt"), ("snap_datasets", "p2p-Gnutella04.txt"), ("snap_datasets", "p2p-Gnutella05.txt"), ("snap_datasets", "p2p-Gnutella06.txt"), ("snap_datasets", "p2p-Gnutella08.txt"), ("snap_datasets", "p2p-Gnutella09.txt"), ("snap_datasets", "p2p-Gnutella24.txt"), ("snap_datasets", "p2p-Gnutella25.txt"), ("snap_datasets", "p2p-Gnutella30.txt"), ("snap_datasets", "p2p-Gnutella31.txt")]
SMALL_DATASETS = [('snap_datasets', 'ca-HepPh.txt'), ('snap_datasets', 'email-EuAll.txt'), ('snap_datasets', 'wiki-Vote.txt'), ('snap_datasets', 'ca-GrQc.txt'), ('snap_datasets', 'ca-AstroPh.txt'), ('snap_datasets', 'p2p-Gnutella04.txt'), ('snap_datasets', 'p2p-Gnutella05.txt'), ('snap_datasets', 'p2p-Gnutella06.txt'), ('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'p2p-Gnutella25.txt'), ('snap_datasets', 'p2p-Gnutella31.txt'), ('snap_datasets', 'p2p-Gnutella30.txt'), ('snap_datasets', 'p2p-Gnutella24.txt'), ('snap_datasets', 'email-Enron.txt'), ('snap_datasets', 'ca-HepTh.txt'), ('snap_datasets', 'soc-Slashdot0902.txt'), ('snap_datasets', 'p2p-Gnutella08.txt'), ('snap_datasets', 'p2p-Gnutella09.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('snap_datasets', 'soc-Slashdot0811.txt'), ('snap_datasets', 'ca-CondMat.txt')]

import time


from src.algorithms.c5_search import degeneracy_c5_search, find_c5s_slow, remove_degree_1_vertices
from src.data_io.to_csv import c5s_run_and_write

import cProfile
import pstats


def closed_neighborhood(nodes, G):
    """
    Given a tuple (or list/set) of nodes and a Graph object G,
    return the closed neighborhood of those nodes.

    The closed neighborhood N[S] is defined as:
        N[S] = S ∪ { all neighbors of nodes in S }

    Args:
        nodes (tuple[int]): nodes whose closed neighborhood to compute
        G (Graph): custom Graph object (wrapper around networkx.Graph)

    Returns:
        set[int]: set of nodes in the closed neighborhood
    """
    if not nodes:
        return set()

    closed = set(nodes)
    for node in nodes:
        try:
            closed.update(G.neighbors(node))
        except Exception as e:
            raise ValueError(f"Node {node} not found in graph: {e}")
    return closed


def main():
    # Get data
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    for dataset in small_datasets[8:]:
    # for dataset in C5_LOCATING_SETS:

        graph = graph_load_fn_map[dataset]()\
        

        print("\n")
        graph.report_sizes()
        print("")

        # First we need to do a search for all the c5s in the Graph
        # ================   FINDING C5s   ==================== #
        start = time.perf_counter()

        c5s = degeneracy_c5_search(graph)
        print(f"Found {len(c5s)} in {graph.name}")
        if (len(c5s) < 20): print(f"\t{c5s}")


        end = time.perf_counter()
        print(f"\tElapsed: {end - start:.6f} seconds")
        
        # Now we want to compose a list of the closed neighborhoods of the c5s
        # ================   CALCULATING NEIGHBORHOODS   ==================== #
        start = time.perf_counter()

        c5s = list(c5s) # Wrap in a list for iterating over and storing indices
        c5_neighborhoods = []

        for c5 in c5s:
            c5_neighborhoods.append(closed_neighborhood(c5, graph))

        # Then we want to remove the N[c5s], while keeping a bound counter

        # ================   ANALYZING NEIGHBORHOOD DISTRIBUTIONS   ==================== #
        neighborhood_node_counts = []
        neighborhood_edge_counts = []

        for N_c5 in c5_neighborhoods:
            # Record number of nodes in the neighborhood
            neighborhood_node_counts.append(len(N_c5))

            # Get induced subgraph of this neighborhood
            subgraph = graph.subgraph(N_c5)
            neighborhood_edge_counts.append(subgraph.number_of_edges())

        # Print summary stats
        print("\nNeighborhood statistics:")
        print(f"\tAverage |N[C5]| = {sum(neighborhood_node_counts) / len(neighborhood_node_counts):.2f}")
        print(f"\tAverage edges in N[C5] = {sum(neighborhood_edge_counts) / len(neighborhood_edge_counts):.2f}")
        print(f"\tMin/Max |N[C5]| = {min(neighborhood_node_counts)} / {max(neighborhood_node_counts)}")
        print(f"\tMin/Max edges in N[C5] = {min(neighborhood_edge_counts)} / {max(neighborhood_edge_counts)}")

        # ================   VISUALIZING DISTRIBUTIONS   ==================== #
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        plt.suptitle(f"Neighborhood Statistics for {graph.name}")

        # Histogram of neighborhood sizes
        axes[0].hist(neighborhood_node_counts, bins=20, color="skyblue", edgecolor="black")
        axes[0].set_title("Distribution of |N[C5]| (Neighborhood Size)")
        axes[0].set_xlabel("Number of nodes in N[C5]")
        axes[0].set_ylabel("Frequency")

        # Histogram of neighborhood edge counts
        axes[1].hist(neighborhood_edge_counts, bins=20, color="lightcoral", edgecolor="black")
        axes[1].set_title("Distribution of edges in N[C5]")
        axes[1].set_xlabel("Number of edges in N[C5]")
        axes[1].set_ylabel("Frequency")

        plt.tight_layout()
        plt.show()
        # ================   REMOVING NEIGHBORHOODS   ==================== #

        



        # We want to compare with the Maximum Independant Set value as a lower bound



        break


    
if __name__ == "__main__":
    main()


