from src.structures.graph import Graph

from src.solvers.tools.reductions import apply_reductions_external, removed_masked_nodes
from src.solvers.tools.external_solvers import find_indepedent_set_size

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