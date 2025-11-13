
from src.data_io.process_data import get_graphs
from src.solvers.reduce_and_bound import reduce_and_bound
from src.solvers.independence_bound import independence_bound


optimal_cover_sizes = {
    "ca-AstroPh": 6760,
    "ca-CondMat": 9612,
    "ca-GrQc": 2459,
    "ca-HepPh": 4996,
    "ca-HepTh": 4896,
    "dblp-2010": 159952,
    "email-EuAll": 246898,
    "p2p-Gnutella04": 6528,
    "p2p-Gnutella05": 5418,
    "p2p-Gnutella06": 5312,
    "p2p-Gnutella08": 4247,
    "p2p-Gnutella09": 5540,
    "p2p-Gnutella24": 19309,
    "p2p-Gnutella25": 16670,
    "p2p-Gnutella30": 27414,
    "p2p-Gnutella31": 46893,
    "soc-Slashdot0811": 53314,
    "wiki-Vote": 4866,
    "dblp-2011": 487356,
    "email-Enron": 22256,
    "flickr-growth": 1662026,
    "flickr-links": 1240632,
    "hollywood-2009": 249867,
    "hollywood-2011": 523403,
    "petster-carnivore": 252577,
    "petster-friendships-cat": 108597,
    "soc-Epinions1": 53599,
    "soc-Slashdot0902": 56398,
    "web-Google": 529222,
    "wiki-Talk": 338222,
    "youtube-links": 860379,
    "youtube-u-growth": 2383596,
    "zhishi-baidu-internallink": 1504379
}


# === DATA SETS === #
C5_LOCATING_SETS = [("test_datasets", "c5.txt"),("test_datasets", "c5_1.txt"), ("test_datasets", "locate_c5_small.txt"), ("test_datasets", "locate_c5_small2.txt"), ("test_datasets", "katate.txt")]
DEGEN_TEST_DATASETS = [("snap_datasets", "ca-GrQc.txt"), ("snap_datasets","ca-HepTh.txt"), ("snap_datasets", "p2p-Gnutella04.txt"), ("snap_datasets", "p2p-Gnutella05.txt"), ("snap_datasets", "p2p-Gnutella06.txt"), ("snap_datasets", "p2p-Gnutella08.txt"), ("snap_datasets", "p2p-Gnutella09.txt"), ("snap_datasets", "p2p-Gnutella24.txt"), ("snap_datasets", "p2p-Gnutella25.txt"), ("snap_datasets", "p2p-Gnutella30.txt"), ("snap_datasets", "p2p-Gnutella31.txt")]
SMALL_DATASETS = [('snap_datasets', 'ca-HepPh.txt'), ('snap_datasets', 'email-EuAll.txt'), ('snap_datasets', 'wiki-Vote.txt'), ('snap_datasets', 'ca-GrQc.txt'), ('snap_datasets', 'ca-AstroPh.txt'), ('snap_datasets', 'p2p-Gnutella04.txt'), ('snap_datasets', 'p2p-Gnutella05.txt'), ('snap_datasets', 'p2p-Gnutella06.txt'), ('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'p2p-Gnutella25.txt'), ('snap_datasets', 'p2p-Gnutella31.txt'), ('snap_datasets', 'p2p-Gnutella30.txt'), ('snap_datasets', 'p2p-Gnutella24.txt'), ('snap_datasets', 'email-Enron.txt'), ('snap_datasets', 'ca-HepTh.txt'), ('snap_datasets', 'soc-Slashdot0902.txt'), ('snap_datasets', 'p2p-Gnutella08.txt'), ('snap_datasets', 'p2p-Gnutella09.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('snap_datasets', 'soc-Slashdot0811.txt'), ('snap_datasets', 'ca-CondMat.txt')]

from functools import partial

# === REDUCTION FUNCTIONS === #
from src.algorithms.reductions import apply_reductions, apply_reductions_external
apply_reductions.__name__           = "apply_reductions"
apply_reductions_external.__name__  = "apply_reductions_external"

# === HEURISTIC FUNCTIONS === #
from src.solvers.tools.subgraph_heuristics import (
    smallest_neighborhood,
    largest_neighborhood,
    random_neighborhood
)
smallest_neighborhood.__name__  = "smallest_neighborhood"
largest_neighborhood.__name__   = "largest_neighborhood"
random_neighborhood.__name__    = "random_neighborhood"

# === NEIGHBORHOOD BOUNDERS === #
from src.solvers.tools.evaluate_subgraph import (
    clique_cover_neighborhood_bound,
    independence_neighborhood_bound,
    trivial_neighborhood_bound
)
clique_cover_neighborhood_bound.__name__    = "clique_cover_neighborhood_bound"
independence_neighborhood_bound.__name__    = "independence_neighborhood_bound"
trivial_neighborhood_bound.__name__         = "trivial_neighborhood_bound"

# === AUXILIARY SOLVERS === #
from src.solvers.tools.external_solvers import find_indepedent_set_size
find_indepedent_set_size.__name__ = "find_indepedent_set_size"


def setup_algorithm(
    base_algorithm=reduce_and_bound,
    reductions=apply_reductions_external,
    heuristic=smallest_neighborhood,
    neighborhood_bound=trivial_neighborhood_bound,
    auxiliary_bounder=find_indepedent_set_size
):
    rab_result = partial(
        base_algorithm,
        reductions=reductions,
        heuristic=heuristic,
        neighborhood_bound=neighborhood_bound,
        auxiliary_bounder=auxiliary_bounder
    )

    # Construct a readable name summarizing configuration
    rab_result.__name__ = (
        f"{base_algorithm.__name__}("
        f"reductions={reductions.__name__}, "
        f"heuristic={heuristic.__name__}, "
        f"neighborhood_bound={neighborhood_bound.__name__}, "
        f"auxiliary_bounder={auxiliary_bounder.__name__})"
    )

    return rab_result



# ======== PARTIALLY INSTANTIATED ALGORITHMS ======== #
from functools import partial

# Default for Independence Bound:
ib_default = partial(independence_bound, reductions=apply_reductions_external)
ib_default.__name__ = "ib_default_v1"

rab_simple1 = setup_algorithm(reductions=apply_reductions_external,
                              heuristic=smallest_neighborhood,
                              neighborhood_bound=trivial_neighborhood_bound,
                              auxiliary_bounder=find_indepedent_set_size)

rab_v1 = setup_algorithm(reductions=apply_reductions_external,
                        heuristic=smallest_neighborhood,
                        neighborhood_bound=independence_neighborhood_bound,
                        auxiliary_bounder=find_indepedent_set_size)

rab_v2 = setup_algorithm(reductions=apply_reductions_external,
                        heuristic=largest_neighborhood,
                        neighborhood_bound=independence_neighborhood_bound,
                        auxiliary_bounder=find_indepedent_set_size)

rab_v3 = setup_algorithm(reductions=apply_reductions_external,
                        heuristic=largest_neighborhood,
                        neighborhood_bound=clique_cover_neighborhood_bound,
                        auxiliary_bounder=find_indepedent_set_size)



from src.data_analysis.compare_bounds import evaluate_bounds_on_datasets, compare_to_optimal

def main():
    # Get data
    # too_slow_15 = [('snap_datasets', 'cit-HepTh.txt'), ('snap_datasets', 'cit-HepPh.txt'), ('new_snap_datasets', 'roadNet-CA.txt'), ('new_snap_datasets', 'roadNet-TX.txt'), ('new_snap_datasets', 'web-BerkStan.txt')]
    too_slow_60 = [('new_snap_datasets', 'web-BerkStan.txt')]
    small_non_optimally_bounded = ('snap_datasets', 'email-Enron.txt')
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()

    testing_sets = [dataset for dataset in large_datasets if dataset not in too_slow_60] + [small_non_optimally_bounded]

    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rab_simple1,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path="bounds_results.csv")
    
    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rab_v1,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path="bounds_results_v1.csv")
    
    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rab_v2,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path="bounds_results_v2.csv")
    
    # evaluate_bounds_on_datasets(datasets        = testing_sets,
    #                             rab_algorithm   = rab_v3,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path="bounds_results_v3.csv")

    # evaluate_bounds_on_datasets(datasets        = small_datasets+large_datasets,
    #                             rab_algorithm   = rab_v2,
    #                             ib_algorithm    = ib_default,
    #                             timeout         = 60,
    #                             output_path="bounds_results_v2_all.csv")

    compare_to_optimal("bounds_results_v2_all.csv", optimal_cover_sizes, "\t")

    
if __name__ == "__main__":
    main()


