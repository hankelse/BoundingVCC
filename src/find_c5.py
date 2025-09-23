from data_io.load_data import load_lazy
from data_io.process_data import get_graphs
from algorithms.degeneracy import get_degeneracy
from algorithms.slow_degeneracy import get_degeneracy_slow
from graph import Graph


from pprint import pprint
import time
import itertools
import networkx as nx




C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [("snap_datasets", "ca-GrQc.txt"), ("snap_datasets","ca-HepTh.txt"), ("snap_datasets", "p2p-Gnutella04.txt"), ("snap_datasets", "p2p-Gnutella05.txt"), ("snap_datasets", "p2p-Gnutella06.txt"), ("snap_datasets", "p2p-Gnutella08.txt"), ("snap_datasets", "p2p-Gnutella09.txt"), ("snap_datasets", "p2p-Gnutella24.txt"), ("snap_datasets", "p2p-Gnutella25.txt"), ("snap_datasets", "p2p-Gnutella30.txt"), ("snap_datasets", "p2p-Gnutella31.txt")]
# # C5_LOCATING_SETS = [("test_datasets", "c5.txt")]
# # C5_LOCATING_SETS = [("test_datasets", "locate_c5_small.txt")]
# # C5_LOCATING_SETS = [("test_datasets", "locate_c5_small2.txt")]
# # C5_LOCATING_SETS = [("test_datasets", "katate_smaller.txt")]
# C5_LOCATING_SETS = [("test_datasets", "katate.txt")]

import time


from algorithms.c5_search import degeneracy_c5_search, find_c5s_slow
from data_io.to_csv import c5s_run_and_write

def main():
    # Get data
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    c5s_run_and_write(DEGEN_TEST_DATASETS, degeneracy_c5_search, attempt_timeout=180)




    # # for dataset in C5_LOCATING_SETS:
    # for dataset in DEGEN_TEST_DATASETS:
    #     graph = graph_load_fn_map[dataset]()
    #     print("\n")
    #     graph.report_sizes()
    #     print("")

    #     start = time.perf_counter()
    #     check_c5s = find_c5s_slow(graph)
    #     print(f"There SHOULD BE {len(check_c5s)} in {graph.name}")
    #     if (len(check_c5s) < 20): print(f"\t{check_c5s}")
    #     # print(f"\tThey are {c5s}")
    #     end = time.perf_counter()
    #     print(f"\tElapsed: {end - start:.6f} seconds")

        
    #     start = time.perf_counter()
    #     c5s = degeneracy_c5_search(graph)
    #     print(f"We FOUND {len(c5s)} in {graph.name}")
    #     if (len(c5s) < 20): print(f"\tThey are {c5s}")
    #     end = time.perf_counter()
    #     print(f"\tElapsed: {end - start:.6f} seconds")



    #     # graph.show()


    #     if len(c5s) != len(check_c5s):

    #         if len(c5s) < len(check_c5s):
    #             c5s_list = []
    #             for c5 in c5s:
    #                 c5_sort = sorted(c5)
    #                 c5s_list.append(c5_sort)
    #             c5s_list = sorted(c5s_list)

    #             c5s_check_list = []
    #             for c5 in check_c5s:
    #                 c5_sort = sorted(c5)
    #                 c5s_check_list.append(c5_sort)
    #             c5s_check_list = sorted(c5s_check_list)

    #             print(f"found    C5s = {c5s_list}")
    #             print(f"correct  C5s = {c5s_check_list}")

    #             for i, c5 in enumerate(c5s_check_list):
    #                 if c5 != c5s_list[i]:
    #                     print(f"{c5} was not found")
    #                     break
    #                     # for node_id in c5:
    #         else:
    #             c5s_list = []
    #             for c5 in c5s:
    #                 c5_sort = sorted(c5)
    #                 c5s_list.append(c5_sort)
    #             c5s_list = sorted(c5s_list)

    #             found_duplicate = False
    #             for i, c5 in enumerate(c5s_list[1::]):
    #                 if c5s_list.count(c5) > 1:
    #                     print(f"Found {c5s_list.count(c5)} copies of : {c5}")
    #                     found_duplicate = True
    #                     break

    #                 # if c5 == c5s_list[i-1]: 
    #                 #     print(f"DUPLICATE: {c5}")
    #                 #     found_duplicate = True

    #             if not found_duplicate:
    #                 print("No duplicates found")

    #                 c5s_check_list = []
    #                 for c5 in check_c5s:
    #                     c5_sort = sorted(c5)
    #                     c5s_check_list.append(c5_sort)
    #                 c5s_check_list = sorted(c5s_check_list)

    #                 print("Looking for a missing graph")
    #                 matched = 0
    #                 for c5 in c5s_list:
    #                     if c5 not in c5s_check_list:
    #                         print("\tfound")
    #                         h = nx.induced_subgraph(graph.nx_graph(), list(c5))
    #                         h = Graph(h.edges())
    #                         h.show()
    #                     else:
    #                         matched += 1
    #                         # c5s_check_list.remove(c5)
    #                 print(f"{matched} out of {len(c5s_list)} matched by {len(c5s_check_list)} c5s in check list.")



    
if __name__ == "__main__":
    main()


