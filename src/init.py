from src.data_io.load_data import load_lazy
from src.data_io.process_data import get_graphs
from src.algorithms.degeneracy import get_degeneracy
from src.algorithms.slow_degeneracy import get_degeneracy_slow
from src.graph import Graph

from src.algorithms.calculating_bounds import closed_neighborhood


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

from src.algorithms.calculating_bounds import reduce_and_bound, independence_bound
import random


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

def main():
    # Get data
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    # for dataset in small_datasets[6:]:
    for dataset in datasets:
        if dataset != ('snap_datasets', 'email-Enron.txt'): continue

        graph = graph_load_fn_map[dataset]()
        

        print("\n")
        graph.report_sizes()
        print("")


        # reduced_graph, offset, clique_cover = reduce_and_bound(graph, heuristic=smallest_neighborhood)
        # print(f"Finished reduce and bound. \n\t Leftover Graph: {reduced_graph.number_of_nodes()} nodes and {reduced_graph.number_of_edges()} edges")
        # print(f"\t Found {len(clique_cover)} cliques with a minimum of {offset} more cliques from removing N[c5s].")

        rab_bound = reduce_and_bound(graph, heuristic=smallest_neighborhood)
        

        i_bound = independence_bound(graph)


        print(f"Found a bound of {rab_bound} using c5_removal bound")
        print(f"Found a bound of {i_bound} using independence bound")



        break


    
if __name__ == "__main__":
    main()


