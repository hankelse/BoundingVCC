from src.structures.graph import Graph
from src.solvers.tools.external_solvers import find_clique_cover_size, find_indepedent_set_size, find_clique_cover


# Lower bounding evaluators
def trivial_neighborhood_bound(graph : Graph, c5_neighborhood):
    return 3

# Upper bounding evaluators

def independence_neighborhood_bound(graph : Graph, c5_neighborhood):
    c5_neighborhood_graph = get_subgraph(graph, c5_neighborhood)
    return find_indepedent_set_size(c5_neighborhood_graph)

# def clique_cover_neighborhood_bound(graph : Graph, c5_neighborhood):
#     c5_neighborhood_graph = get_subgraph(graph, c5_neighborhood)
#     return find_clique_cover_size(c5_neighborhood_graph)


def cover_neighborhood(graph, c5_neighborhood):
    subgraph = get_subgraph(graph, c5_neighborhood)
    cover = find_clique_cover(subgraph)
    # Remap to original labels
    remapped_cover = []
    for clique in cover:
        remapped_clique = []
        for node in clique:
            remapped_clique.append(subgraph.new_to_old_labels[node])
        remapped_cover.append(remapped_clique)
    return remapped_cover




# Generic Helpers

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



    