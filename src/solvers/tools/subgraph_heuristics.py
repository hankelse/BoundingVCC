from src.structures.graph import Graph


def smallest_neighborhood(graph : Graph, c5_neighborhoods):
    min_size = len(c5_neighborhoods[0])
    smallest = c5_neighborhoods[0]

    for neighborhood in c5_neighborhoods[1:]:
        size = len(neighborhood)
        if size < min_size:
            min_size = size
            smallest = neighborhood

    return smallest

def largest_neighborhood(graph: Graph, c5_neighborhoods):
    max_size = len(c5_neighborhoods[0])
    largest = c5_neighborhoods[0]

    for neighborhood in c5_neighborhoods[1:]:
        size = len(neighborhood)
        if size > max_size:
            max_size = size
            largest = neighborhood

    return largest

def random_neighborhood(graph: Graph, c5_neighborhoods):
    from random import choice
    return choice(c5_neighborhoods)



# Generic Helpers
def closed_neighborhood(nodes, graph):
    if not nodes:
        return set()

    closed = set(nodes)
    for node in nodes:
        closed.update(graph.neighbors(node))

    return closed