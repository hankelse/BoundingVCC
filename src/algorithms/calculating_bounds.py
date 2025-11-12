from src.algorithms.c5_search import degeneracy_c5_search
from src.graph import Graph

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


def closed_neighborhood(nodes, graph):
    if not nodes:
        return set()

    closed = set(nodes)
    for node in nodes:
        closed.update(graph.neighbors(node))

    return closed



from src.algorithms.reductions import apply_reductions, removed_masked_nodes, apply_reductions_external
from external_solvers.run_redumis import redumis


def find_indepedent_set_size(graph : Graph):
    if graph.number_of_nodes() == 0: return 0

    graph.write(output_path="temp.txt", file_type="metis")
    result = redumis(graph_path="temp.txt")

    print(f"Independent Set Size: {result['mis_size']}")

    return result['mis_size']

from external_solvers.run_reduvcc import reduvcc  # your new parser

def find_clique_cover_size(graph):
    """
    Runs ReduVCC on the given graph and returns the clique cover size.
    The graph is first written to a temporary METIS file.
    """
    if graph.number_of_nodes() == 0: return 0

    graph.write(output_path="temp.txt", file_type="metis")

    result = reduvcc(graph_path="temp.txt")
    cover_size = None
    if "details" in result and "clique_cover_size" in result["details"]:
        cover_size = result["details"]["clique_cover_size"]

    # print(f"Clique Cover Size: {cover_size}")

    return cover_size




def independence_bound(graph: Graph, reductions=apply_reductions_external):
    # 1) ======== DATA REDUCTIONS ===== #
    masked_nodes, cliques = reductions(graph)
    reduced = removed_masked_nodes(graph, masked_nodes)
    clique_cover = cliques

    print(f"Applied Reductions: {graph.number_of_nodes()} --> {reduced.number_of_nodes()}, found {len(cliques)} cliques.")

    # 2) ======= Run KaMIS to find an indepdendent set bound ==== #
    independent_set_size = find_indepedent_set_size(reduced)

    # 3) ======= Return
    return len(clique_cover) + independent_set_size


# Heuristics
def smallest_neighborhood(graph : Graph, c5_neighborhoods):
    min_size = len(c5_neighborhoods[0])
    smallest = c5_neighborhoods[0]

    for neighborhood in c5_neighborhoods[1:]:
        size = len(neighborhood)
        if size < min_size:
            min_size = size
            smallest = neighborhood

    return smallest

def largest_neighborhood(graph: Graph, c5_neighborhoods):
    max_size = len(c5_neighborhoods[0])
    largest = c5_neighborhoods[0]

    for neighborhood in c5_neighborhoods[1:]:
        size = len(neighborhood)
        if size > max_size:
            max_size = size
            largest = neighborhood

    return largest

def random_neighborhood(graph: Graph, c5_neighborhoods):
    from random import choice
    return choice(c5_neighborhoods)

# Methods of calculating a lower bound on a N[c5]

# Helper
def get_subgraph(graph: Graph, node_subset):
    """
    Returns the induced subgraph of `graph` on the given node list.
    """
    node_subset = set(node_subset)  # Faster lookups

    # Build edge list of edges (u, v) where both endpoints are in the subset
    edge_list = []
    for u in node_subset:
        for v in graph.neighbors(u):
            if v in node_subset and u < v:  # u < v to avoid duplicates
                edge_list.append((u, v))

    # Construct new Graph from these edges
    subgraph = Graph(edge_list)
    return subgraph

def trivial_neighborhood_bound(graph : Graph, c5_neighborhood):
    return 3

def independence_neighborhood_bound(graph : Graph, c5_neighborhood):
    c5_neighborhood_graph = get_subgraph(graph, c5_neighborhood)
    return find_indepedent_set_size(c5_neighborhood_graph)

def clique_cover_neighborhood_bound(graph : Graph, c5_neighborhood):
    c5_neighborhood_graph = get_subgraph(graph, c5_neighborhood)
    return find_clique_cover_size(c5_neighborhood_graph)


def reduce_and_bound(graph: Graph, 
                     reductions=apply_reductions_external,
                     heuristic=smallest_neighborhood, 
                     neighborhood_bound=trivial_neighborhood_bound, 
                     auxiliary_bounder=find_indepedent_set_size,
                     clique_cover=None, 
                     offset = 0):
    
    if clique_cover == None: clique_cover = []
    
    '''
    Takes a graph and applies data reductions until it can't anymore.
    Then, uses an heuristic h, to choose a c5 in the graph to remove
    Then, removes N[c5] and increments an offset by 3
    Then, repeats until there is no more c5 and no more reductions
    '''

    # 1) ======== DATA REDUCTIONS ===== #
    masked_nodes, cliques = reductions(graph)
    reduced = removed_masked_nodes(graph, masked_nodes)
    clique_cover += cliques

    if reduced.number_of_edges() >= 5: # If there can be a c5
        print(f"Applied Reductions: {graph.number_of_nodes()} --> {reduced.number_of_nodes()}, found {len(cliques)} cliques.")

        # 2) ======== C5 SEARCH ===== #
        c5s = degeneracy_c5_search(reduced)
        print(f"Preformed c5 search: {len(c5s)} c5s.")

    else:
        c5s = []

    # 3) ======= CHECK BASE CASE ====== #
    found_c5s = len(c5s) != 0
    if found_c5s:

        # 4) ======= GET N[C5s] ====== #
        c5s = list(c5s) # Wrap in a list for iterating over and storing indices
        c5_neighborhoods = []
        for c5 in c5s:
            c5_neighborhoods.append(closed_neighborhood(c5, reduced))
        print(f"Expanded c5s to N[c5s]")

        # 5) ======= REMOVE A C5 ====== #
        chosen = heuristic(reduced, c5_neighborhoods)
        neighborhood_removal_mask = [False] * reduced.number_of_nodes()
        for node in chosen:
            neighborhood_removal_mask[node] = True
        offset += neighborhood_bound(reduced, chosen)
        print(f"just got an offset of neighborhood of: ", neighborhood_bound(reduced, chosen))
        next_graph = removed_masked_nodes(reduced, neighborhood_removal_mask)

        # 6) ======= RECUR ===== #

        return reduce_and_bound(next_graph, reductions=reductions, heuristic=heuristic, neighborhood_bound=neighborhood_bound, clique_cover=clique_cover, auxiliary_bounder=auxiliary_bounder, offset=offset)
    
    else: # No c5s found --> Run Auxilary Bounder

        # 7) ======= RUN auxilary bounder ===== #
        lower_bound_remaining_graph = auxiliary_bounder(reduced)
        bound = lower_bound_remaining_graph + offset + len(clique_cover)
        return bound

    














