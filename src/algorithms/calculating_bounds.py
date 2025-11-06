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



from src.algorithms.reductions import apply_reductions, removed_masked_nodes
from external_solvers.run_redumis import redumis


def find_indepedent_set_size(graph : Graph):
    graph.write(output_path="temp.txt", file_type="metis")
    result = redumis(graph_path="temp.txt")

    print(f"Independent Set Size: {result['mis_size']}")

    return result['mis_size']



def independence_bound(graph: Graph):
    # 1) ======== DATA REDUCTIONS ===== #
    masked_nodes, cliques = apply_reductions(graph)
    reduced = removed_masked_nodes(graph, masked_nodes)
    clique_cover = cliques

    print(f"Applied Reductions: {graph.number_of_nodes()} --> {reduced.number_of_nodes()}, found {len(cliques)} cliques.")

    # 2) ======= Run KaMIS to find an indepdendent set bound ==== #
    independent_set_size = find_indepedent_set_size(reduced)

    # 3) ======= Return

    return len(clique_cover) + independent_set_size



def reduce_and_bound(graph: Graph, heuristic, clique_cover=[], offset = 0):
    
    '''
    Takes a graph and applies data reductions until it can't anymore.
    Then, uses an heuristic h, to choose a c5 in the graph to remove
    Then, removes N[c5] and increments an offset by 3
    Then, repeats until there is no more c5 and no more reductions
    '''

    # 1) ======== DATA REDUCTIONS ===== #
    masked_nodes, cliques = apply_reductions(graph)
    reduced = removed_masked_nodes(graph, masked_nodes)
    clique_cover += cliques

    print(f"Applied Reductions: {graph.number_of_nodes()} --> {reduced.number_of_nodes()}, found {len(cliques)} cliques.")

    # 2) ======== C5 SEARCH ===== #
    c5s = degeneracy_c5_search(reduced)
    print(f"Preformed c5 search: {len(c5s)} c5s.")

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
        offset += 3
        next_graph = removed_masked_nodes(reduced, neighborhood_removal_mask)

        # 6) ======= RECUR ===== #

        return reduce_and_bound(next_graph, heuristic, clique_cover, offset)
    
    else: # No c5s found --> Run IS
        # 6) ======= RUN reduMIS ===== #

        independent_set_size = find_indepedent_set_size(reduced)

        bound = independent_set_size + offset + len(clique_cover)
        return bound
        # return reduced, offset, clique_cover
    














