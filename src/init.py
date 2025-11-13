
from src.data_io.process_data import get_graphs
from src.solvers.reduce_and_bound import reduce_and_bound
from src.solvers.independence_bound import independence_bound


# === DATA SETS === #
C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [("snap_datasets", "ca-GrQc.txt"), ("snap_datasets","ca-HepTh.txt"), ("snap_datasets", "p2p-Gnutella04.txt"), ("snap_datasets", "p2p-Gnutella05.txt"), ("snap_datasets", "p2p-Gnutella06.txt"), ("snap_datasets", "p2p-Gnutella08.txt"), ("snap_datasets", "p2p-Gnutella09.txt"), ("snap_datasets", "p2p-Gnutella24.txt"), ("snap_datasets", "p2p-Gnutella25.txt"), ("snap_datasets", "p2p-Gnutella30.txt"), ("snap_datasets", "p2p-Gnutella31.txt")]
SMALL_DATASETS = [('snap_datasets', 'ca-HepPh.txt'), ('snap_datasets', 'email-EuAll.txt'), ('snap_datasets', 'wiki-Vote.txt'), ('snap_datasets', 'ca-GrQc.txt'), ('snap_datasets', 'ca-AstroPh.txt'), ('snap_datasets', 'p2p-Gnutella04.txt'), ('snap_datasets', 'p2p-Gnutella05.txt'), ('snap_datasets', 'p2p-Gnutella06.txt'), ('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'p2p-Gnutella25.txt'), ('snap_datasets', 'p2p-Gnutella31.txt'), ('snap_datasets', 'p2p-Gnutella30.txt'), ('snap_datasets', 'p2p-Gnutella24.txt'), ('snap_datasets', 'email-Enron.txt'), ('snap_datasets', 'ca-HepTh.txt'), ('snap_datasets', 'soc-Slashdot0902.txt'), ('snap_datasets', 'p2p-Gnutella08.txt'), ('snap_datasets', 'p2p-Gnutella09.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('snap_datasets', 'soc-Slashdot0811.txt'), ('snap_datasets', 'ca-CondMat.txt')]

from functools import partial

# === REDUCTION FUNCTIONS === #
from src.algorithms.reductions import apply_reductions, apply_reductions_external
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
    clique_cover_neighborhood_bound,
    independence_neighborhood_bound,
    trivial_neighborhood_bound
)
# = Cover calculating = #
clique_cover_neighborhood_bound.__name__    = "clique_cover_neighborhood_bound"
independence_neighborhood_bound.__name__    = "independence_neighborhood_bound"

# = Lower bounding = #
trivial_neighborhood_bound.__name__         = "trivial_neighborhood_bound"

# === AUXILIARY SOLVERS === #
from src.solvers.tools.external_solvers import find_indepedent_set_size
find_indepedent_set_size.__name__ = "find_indepedent_set_size"


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

# First Reduce and Bound Algorithm
rab_v1 = setup_algorithm(name="reduce_and_bound_v1",
                        base_algorithm=reduce_and_bound,
                        reductions=apply_reductions_external,
                        pattern_finder=degeneracy_c5_search,
                        heuristic=smallest_neighborhood,
                        neighborhood_evaluator=trivial_neighborhood_bound,
                        auxiliary_solver=find_indepedent_set_size)


from src.data_analysis.compare_bounds import evaluate_bounds_on_datasets, compare_to_optimal

def main():
    # Get data
    # too_slow_15 = [('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('new_snap_datasets', 'roadNet-CA.txt'), ('new_snap_datasets', 'roadNet-TX.txt'), ('new_snap_datasets', 'web-BerkStan.txt')]
    too_slow_60 = [('new_snap_datasets', 'web-BerkStan.txt')]
    small_non_optimally_bounded = ('snap_datasets', 'email-Enron.txt')
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    testing_sets = [dataset for dataset in large_datasets if dataset not in too_slow_60] + [small_non_optimally_bounded]
    testing_sets = [small_non_optimally_bounded]
    
    evaluate_bounds_on_datasets(datasets        = testing_sets,
                                rab_algorithm   = rab_v1,
                                ib_algorithm    = ib_default,
                                timeout         = 60,
                                output_path="bounds_results_v1.csv")
    


    # compare_to_optimal("bounds_results_v2_all.csv", optimal_cover_sizes, "\t")

    
if __name__ == "__main__":
    main()


