from data_io.load_data import load_lazy
from data_io.process_data import get_graphs
from algorithms.degeneracy import get_degeneracy
from algorithms.slow_degeneracy import get_degeneracy_slow
from graph import Graph


from pprint import pprint
import time
import itertools
import networkx as nx




C5_LOCATING_SETS = [("test_datasets", "c5.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [ ("snap_datasets", "ca-GrQc.txt"), 
                        ("snap_datasets","ca-HepTh.txt"),     
                        ("snap_datasets", "p2p-Gnutella04.txt"),
                        ("snap_datasets", "p2p-Gnutella05.txt"),
                        ("snap_datasets", "p2p-Gnutella06.txt"),
                        ("snap_datasets", "p2p-Gnutella08.txt"),
                        ("snap_datasets", "p2p-Gnutella09.txt"),
                        ("snap_datasets", "p2p-Gnutella24.txt"),
                        ("snap_datasets", "p2p-Gnutella25.txt"),
                        ("snap_datasets", "p2p-Gnutella30.txt"),
                        ("snap_datasets", "p2p-Gnutella31.txt")]
# C5_LOCATING_SETS = [("test_datasets", "locate_c5_small2.txt")]


import time



def main():
    # Get data
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    # for dataset in C5_LOCATING_SETS:
    for dataset in DEGEN_TEST_DATASETS:
        graph = graph_load_fn_map[dataset]()

        graph.report_sizes()
        start = time.perf_counter()
        end = time.perf_counter()
        print(f"Elapsed: {end - start:.6f} seconds for slow degeneracy calculation")
        

        graph.show()
    

    
main()


