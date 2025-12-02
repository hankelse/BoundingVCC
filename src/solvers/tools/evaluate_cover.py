from src.structures.graph import Graph


def validate_cover(graph : Graph, cover):

    valid_covering = True
    missing_edges = []
    uncovered_nodes = []
    is_covered = [False] * graph.number_of_nodes()

    for clique in cover:

        # mark vertices as covered
        for v in clique:
            is_covered[v] = True

        # check clique edges
        for i in range(len(clique)):
            v = clique[i]
            for j in range(i + 1, len(clique)):
                u = clique[j]
                if not graph.has_edge(v, u):
                    missing_edges.append((v, u))
                    valid_covering = False

    
    for node in graph.nodes():
        if not is_covered[node]:
            uncovered_nodes.append(node)
            valid_covering = False
    
    return valid_covering, missing_edges, uncovered_nodes
    








