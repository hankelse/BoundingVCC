from src.structures.graph import Graph


def smallest_neighborhood(graph : Graph, c5s):
    min_size = len(closed_neighborhood(c5s[0], graph))
    smallest = c5s[0]

    for neighborhood in c5s[1:]:
        closed_nh = closed_neighborhood(neighborhood)
        size = len(closed_nh)
        if size < min_size:
            min_size = size
            smallest = closed_nh

    return smallest

def largest_neighborhood(graph : Graph, c5s):
    max_size = len(closed_neighborhood(c5s[0], graph))
    largest = c5s[0]

    for neighborhood in c5s[1:]:
        closed_nh = closed_neighborhood(neighborhood)
        size = len(closed_nh)
        if size > max_size:
            max_size = size
            largest = closed_nh
    return largest


def random_neighborhood(graph: Graph, c5s):
    from random import choice
    c5 = choice(c5s)
    return closed_neighborhood(c5)



# Generic Helpers
def closed_neighborhood(nodes, graph):
    if not nodes:
        return set()

    closed = set(nodes)
    for node in nodes:
        closed.update(graph.neighbors(node))

    return closed