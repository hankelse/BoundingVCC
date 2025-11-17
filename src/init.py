
from src.data_io.process_data import get_graphs
from src.solvers.reduce_and_bound import reduce_and_bound
from src.solvers.reduce_and_peel import reduce_and_peel
from src.solvers.independence_bound import independence_bound


# === DATA SETS === #
C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [("snap_datasets", "ca-GrQc.txt"), ("snap_datasets","ca-HepTh.txt"), ("snap_datasets", "p2p-Gnutella04.txt"), ("snap_datasets", "p2p-Gnutella05.txt"), ("snap_datasets", "p2p-Gnutella06.txt"), ("snap_datasets", "p2p-Gnutella08.txt"), ("snap_datasets", "p2p-Gnutella09.txt"), ("snap_datasets", "p2p-Gnutella24.txt"), ("snap_datasets", "p2p-Gnutella25.txt"), ("snap_datasets", "p2p-Gnutella30.txt"), ("snap_datasets", "p2p-Gnutella31.txt")]
SMALL_DATASETS = [('snap_datasets', 'ca-HepPh.txt'), ('snap_datasets', 'email-EuAll.txt'), ('snap_datasets', 'wiki-Vote.txt'), ('snap_datasets', 'ca-GrQc.txt'), ('snap_datasets', 'ca-AstroPh.txt'), ('snap_datasets', 'p2p-Gnutella04.txt'), ('snap_datasets', 'p2p-Gnutella05.txt'), ('snap_datasets', 'p2p-Gnutella06.txt'), ('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'p2p-Gnutella25.txt'), ('snap_datasets', 'p2p-Gnutella31.txt'), ('snap_datasets', 'p2p-Gnutella30.txt'), ('snap_datasets', 'p2p-Gnutella24.txt'), ('snap_datasets', 'email-Enron.txt'), ('snap_datasets', 'ca-HepTh.txt'), ('snap_datasets', 'soc-Slashdot0902.txt'), ('snap_datasets', 'p2p-Gnutella08.txt'), ('snap_datasets', 'p2p-Gnutella09.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('snap_datasets', 'soc-Slashdot0811.txt'), ('snap_datasets', 'ca-CondMat.txt')]

from functools import partial

# === REDUCTION FUNCTIONS === #
from src.solvers.tools.reductions import apply_reductions, apply_reductions_external
apply_reductions.__name__           = "apply_reductions"
apply_reductions_external.__name__  = "apply_reductions_external"

# === PATTERN FINDERS === #
from src.algorithms.c5_search import degeneracy_c5_search

# === HEURISTIC FUNCTIONS === #
from src.solvers.tools.subgraph_heuristics import (
    smallest_neighborhood,
    largest_neighborhood,
    random_neighborhood
)
smallest_neighborhood.__name__  = "smallest_neighborhood"
largest_neighborhood.__name__   = "largest_neighborhood"
random_neighborhood.__name__    = "random_neighborhood"

# === SUBGRAPH EVALUATERS === #
from src.solvers.tools.evaluate_subgraph import (
    # clique_cover_neighborhood_bound,
    independence_neighborhood_bound,
    trivial_neighborhood_bound,
    cover_neighborhood
)
# = Cover calculating = #
# clique_cover_neighborhood_bound.__name__    = "clique_cover_neighborhood_bound"
independence_neighborhood_bound.__name__    = "independence_neighborhood_bound"
cover_neighborhood.__name__ = "clique_cover_neighborhood"

# = Lower bounding = #
trivial_neighborhood_bound.__name__         = "trivial_neighborhood_bound"

# === AUXILIARY SOLVERS === #
from src.solvers.tools.external_solvers import find_indepedent_set_size, find_clique_cover_size
find_indepedent_set_size.__name__ = "find_indepedent_set_size"
find_clique_cover_size.__name__ = "find_clique_cover_size"


def setup_algorithm(
    name,
    base_algorithm,
    reductions=apply_reductions_external,
    pattern_finder=degeneracy_c5_search,
    heuristic=smallest_neighborhood,
    neighborhood_evaluator=trivial_neighborhood_bound,
    auxiliary_solver=find_indepedent_set_size,
    **extra_kwargs
):
    """
    Creates a partially configured version of a reduce-and-act algorithm
    (e.g., reduce_and_bound, reduce_and_peel).

    Returns a callable with attributes:
      - __name__: human-readable name
      - config: dictionary of configuration arguments
    """
    # Create the partially configured callable
    result = partial(
        base_algorithm,
        reductions=reductions,
        pat_finder=pattern_finder,
        pat_choice_heuristic=heuristic,
        pat_neighborhood_evaluator=neighborhood_evaluator,
        auxiliary_solver=auxiliary_solver,
        **extra_kwargs
    )

    # Add metadata for readability and logging
    result.__name__ = name
    result.config = {
        "base_algorithm": base_algorithm.__name__,
        "reductions": reductions.__name__,
        "pattern_finder": pattern_finder.__name__,
        "heuristic": heuristic.__name__,
        "neighborhood_evaluator": neighborhood_evaluator.__name__,
        "auxiliary_solver": auxiliary_solver.__name__,
        **{k: getattr(v, "__name__", str(v)) for k, v in extra_kwargs.items()}
    }

    return result



# ======== PARTIALLY INSTANTIATED ALGORITHMS ======== #
from functools import partial

# Default for Independence Bound:
ib_default = partial(independence_bound, reductions=apply_reductions_external)
ib_default.__name__ = "ib_default_v1"

from src.solvers.reduce_and_bound import ReduceAndBound
from src.solvers.reduce_and_peel import ReduceAndPeel
from src.solvers.independence_bound import independence_bound
from src.solvers.tools.external_solvers import find_clique_cover


# # First Reduce and Bound Algorithm
# rab_v1 = setup_algorithm(name="reduce_and_bound_v1",
#                         base_algorithm=reduce_and_bound,
#                         reductions=apply_reductions_external,
#                         pattern_finder=degeneracy_c5_search,
#                         heuristic=smallest_neighborhood,
#                         neighborhood_evaluator=trivial_neighborhood_bound,
#                         auxiliary_solver=find_indepedent_set_size)

# rap_v1 = setup_algorithm(name = "reduce_and_peel_v1",
#                          base_algorithm=reduce_and_peel,
#                          reductions=apply_reductions_external,
#                          pattern_finder=degeneracy_c5_search,
#                          heuristic=largest_neighborhood,
#                          neighborhood_evaluator=clique_cover_neighborhood_bound,
#                          auxiliary_solver=find_clique_cover_size)


rab_v1 = ReduceAndBound(
        reductions=apply_reductions_external,
        pat_finder=degeneracy_c5_search,
        pat_choice_heuristic=smallest_neighborhood,
        pat_neighborhood_evaluator=trivial_neighborhood_bound,
        auxiliary_solver=independence_bound
    )

rap_v1 = ReduceAndPeel(
    reductions=apply_reductions_external,
    pat_finder=degeneracy_c5_search,
    pat_choice_heuristic=smallest_neighborhood,
    pat_neighborhood_evaluator=cover_neighborhood,
    auxiliary_solver=find_clique_cover
)




from src.data_analysis.compare_bounds import evaluate_bounds_on_datasets, compare_to_optimal
from src.solvers.tools.evaluate_cover import validate_cover

def main():
    # # Get data
    # too_slow_15 = [('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('new_snap_datasets', 'roadNet-CA.txt'), ('new_snap_datasets', 'roadNet-TX.txt'), ('new_snap_datasets', 'web-BerkStan.txt')]
    # too_slow_60 = [('new_snap_datasets', 'web-BerkStan.txt')]
    # small_non_optimally_bounded = ('snap_datasets', 'email-Enron.txt')
    # datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    # testing_sets = [dataset for dataset in large_datasets if dataset not in too_slow_60] + [small_non_optimally_bounded]
    # # testing_sets = [small_non_optimally_bounded]
    
    
    from src.data_io.process_data import path_to_graph
    # g = path_to_graph('snap_datasets', 'email-Enron.txt')
    # g = path_to_graph('test_datasets', 'c5.txt')
    # print(rab_v1.run(g))
    # print(rab_v1.get_log())

    # C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]

    # for a, b, in C5_LOCATING_SETS:
    for a, b, in  [('snap_datasets', 'email-Enron.txt')]:
        rap_v1 = ReduceAndPeel(
            reductions=apply_reductions_external,
            pat_finder=degeneracy_c5_search,
            pat_choice_heuristic=smallest_neighborhood,
            pat_neighborhood_evaluator=cover_neighborhood,
            auxiliary_solver=find_clique_cover
        )


        # print(a, b)
        g = path_to_graph(a, b)
        cliques = rap_v1.run(g)
        valid, missing, uncovered = validate_cover(g, cliques)
        print(valid)
        print(len(missing), len(uncovered))
        # if not valid:
        #     print(a, b)
        #     print(len(missing), len(uncovered))
            # print(missing, uncovered)

            # print(cliques)

    # print(len(cliques))
    # print(rap_v1.get_log())

    # cliques = find_clique_cover(g)


    # g = path_to_graph('snap_datasets', 'email-Enron.txt')
    

    print(rap_v1.get_log())

    # num, cliques = apply_reductions_external(g)
    # print(cliques)

    
    

    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rab_v1,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path=f"{rab_v1.__name__}.csv")
    
    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rap_v1,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path=f"{rap_v1.__name__}.csv")
    


    # compare_to_optimal("bounds_results_v2_all.csv", optimal_cover_sizes, "\t")

    
if __name__ == "__main__":

    # def tracefunc(frame, event, arg, indent=[0]):
    #   if frame.f_code.co_name in ["__iter__", "<genexpr>"]: 
    #     return

    #   if event == "call":
    #       indent[0] += 2
    #       print("-" * indent[0] + "> call function", frame.f_code.co_name)
    #   elif event == "return":
    #       print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
    #       indent[0] -= 2
    #   return tracefunc

    # import sys
    # sys.setprofile(tracefunc)
    main()
    # import networkx as nx
    # import matplotlib.pyplot as plt

    # # --- Raw METIS data as a string ---
    # metis_data = """\
    # 12 13
    # 2 3
    # 1 3
    # 1 2
    # 5 6 7
    # 4 6 7
    # 4 5 7
    # 4 5 6
    # 9 10
    # 8 10
    # 8 9
    # 12
    # 11
    # """

    # # --- Parse the METIS data ---
    # lines = metis_data.strip().splitlines()
    # num_nodes, num_edges = map(int, lines[0].split())

    # G = nx.Graph()

    # # Add nodes explicitly (optional, for clarity)
    # G.add_nodes_from(range(1, num_nodes + 1))

    # # Add edges based on adjacency list
    # for i, line in enumerate(lines[1:], start=1):
    #     if not line.strip():
    #         continue
    #     neighbors = map(int, line.split())
    #     for nbr in neighbors:
    #         # METIS is 1-indexed, so just add (i, nbr)
    #         G.add_edge(i, nbr)

    # # --- Display information ---
    # print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    # print("Edges:", sorted(G.edges()))

    # # --- Draw the graph ---
    # plt.figure(figsize=(6, 5))
    # pos = nx.spring_layout(G, seed=42)
    # nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=600, font_weight="bold")
    # plt.title("Graph Parsed from METIS Data")
    # plt.show()


