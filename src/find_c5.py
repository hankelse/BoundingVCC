from data_io.load_data import load_lazy
from data_io.process_data import get_graphs
from algorithms.degeneracy import get_degeneracy
from graph import Graph


from pprint import pprint
import time
import itertools
import networkx as nx

# Brute force approach
def find_c5s_slow(G):
    """
    Brutish Search for c5s: Runs in O(n * highest_degree^4)
    """
    c5s = set()
    
    for v1 in G.nodes():                               # O(n)      -> O(n)            
        for v2 in G.neighbors(v1):                     # O(\delta) -> O(n\delta)
            for v3 in G.neighbors(v2):                 # O(\delta) -> O(n\delta^2)
                if v3 in (v1, v2): 
                    continue
                for v4 in G.neighbors(v3):             # O(\delta) -> O(n\delta^3)
                    if v4 in (v1, v2, v3):
                        continue
                    for v5 in G.neighbors(v4):         # O(\delta) -> O(n\delta^4)
                        if v5 in (v1, v2, v3, v4):
                            continue
                        # Check if it closes the cycle
                        if G.has_edge(v5, v1):
                            nodes = {v1, v2, v3, v4, v5}
                            if len(nodes) == 5:  # all distinct
                                sub = G.subgraph(nodes)
                                if sub.number_of_edges() == 5:
                                    c5s.add(tuple(nodes))
    return list(c5s)



C5_LOCATING_SETS = [("test_datasets", "c5.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
C5_LOCATING_SETS = [("test_datasets", "locate_c5_small2.txt")]


def main():
    # Get data
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    for dataset in C5_LOCATING_SETS:
        graph = graph_load_fn_map[dataset]()

        graph.report_sizes()

        # Start timer
        start = time.perf_counter()

        # Start the algorithm
        print(find_c5s_slow(graph))

        #End timer
        end = time.perf_counter()

        degen_ordering, degeneracy = get_degeneracy(graph)
        print(degen_ordering, degeneracy)
        
        print(f"Elapsed: {end - start:.6f} seconds")

        graph.show()

main()


