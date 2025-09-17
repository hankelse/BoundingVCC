from algorithms.degeneracy import get_degeneracy, compute_later_neighbors

# Brute force approach
def find_c5s_slow(G):
    """
    Brutish Search for c5s: Runs in O(n * highest_degree^4)
    """
    c5s = set()
    
    for v1 in G.nodes():                               # O(n)      -> O(n)            
        for v2 in G.neighbors(v1):                     # O(\delta) -> O(n\delta)
            for v3 in G.neighbors(v2):                 # O(\delta) -> O(n\delta^2)
                if v3 in (v1, v2): 
                    continue
                for v4 in G.neighbors(v3):             # O(\delta) -> O(n\delta^3)
                    if v4 in (v1, v2, v3):
                        continue
                    for v5 in G.neighbors(v4):         # O(\delta) -> O(n\delta^4)
                        if v5 in (v1, v2, v3, v4):
                            continue
                        # Check if it closes the cycle
                        if G.has_edge(v5, v1):
                            nodes = {v1, v2, v3, v4, v5}
                            if len(nodes) == 5:  # all distinct
                                sub = G.subgraph(nodes)
                                if sub.number_of_edges() == 5:
                                    c5s.add(tuple(nodes))
    return list(c5s)

from graph import Graph
from algorithms.degeneracy import get_degeneracy
from pprint import pprint
from itertools import permutations
from collections import defaultdict

# def degeneracy_c5_search(graph : Graph):
#     # I want to define this as not a list but as somethning from a set of things that would work than have it later decide.
#     c5s = [] 

#     # Get degeneracy ordering in O(n + m)
#     # degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

#     # TRY OUT EVERY VALID DEGEN ORDERING
#     for degeneracy_ordering in permutations([0, 1, 2, 3, 4]):
#         c5s = [] 

#         # Get later neighbors in O(n + m)
#         later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

#         # Make new edge_set where each edge u, v is ordered so that v is a later neighbor of u
#         # First get the node --> degen index list
#         degen_indices = [-1] * graph.number_of_nodes()
#         for degen_index, node in enumerate(degeneracy_ordering):
#             degen_indices[node] = degen_index

#         forward_edges = set()
#         for u, v in graph.edges():
#             u_d_index = degen_indices[u]
#             v_d_index = degen_indices[v]

#             if u_d_index < v_d_index: # If v is a later neighbor of u
#                 forward_edges.add((u, v))
#             else:
#                 forward_edges.add((v, u))


#         # print(f"forward edges:")
#         # pprint(forward_edges)

#         # print(f"later neighbors:")
#         # pprint(later_neighbors)

#         print(f"degen ordering:")
#         pprint(degeneracy_ordering)


#         # Does zero have later neighbors with neighbors? --> type 1, else type 2
#         type1 = True
#         for ln in later_neighbors[0]: 
#             if len(later_neighbors[ln]) == 0: type1 = False
#         if type1: print("type 1")
#         else: print("type 2")

#         # Look for c5s
#         for u, v in forward_edges: # O(m)
#             # print(f"1 u={u}, v={v}")
#             # we know that v is a later neighbor of u

#             # Look at all u --> v --> w
#             for w in later_neighbors[v]: # O(d) --> O(md)
#                 # print(f"2 {u}, {v}, w={w}")
#                 if (u, w) in forward_edges: continue # then u --> v --> w is a cycle so skip to next w

#                 for x in later_neighbors[w]: # O(d) --> O(md^2)
#                     # print(f"3 {u}, {v}, {w}, x={x}")
#                     if (u, x) in forward_edges: 
#                         # print(f"not a cycle! {u, x} is a chord")
#                         continue # then u --> v --> w --> x is a cycle so skip to next x
#                     if (v, x) in forward_edges:
#                         # print(f"not a cycle! {v, x} is a chord")
#                         continue # v --> w --> x is a cycle??
#                     # assume that u --> v --> w --> x
#                     # Is there a y?

#                     for y in later_neighbors[x]:  # ≤ d
#                         if y == u or y == v or y == w:
#                             continue
#                         # Check closure
#                         if (y, u) in forward_edges or (u, y) in forward_edges:
#                             cycle = tuple(sorted([u, v, w, x, y]))
#                             c5s.append(cycle)

                    
                    




#                     # for y in later_neighbors[x]: # O(d) --> O(md^3)
#                     #     print(f"4 {u}, {v}, {w}, {x}, y={y}")
#                     #     if (u, y) in forward_edges: # then this is a cycle if no chords from y to v or w
#                     #         if (v, y) in forward_edges: 
#                     #             print(f"not a cycle! {v, y} is a chord")
#                     #             continue
#                     #         if (w, y) in forward_edges: 
#                     #             print(f"not a cycle! {w, y} is a chord")
#                     #             continue

#                     #         print("found!")

#                     #         c5s.append(set([u, v, w, x, y]))

#         print(f"C5s= {c5s} \n")
#     return c5s


# Only meant to account for type 1.2
def degeneracy_c5_search(graph : Graph):
    # I want to define this as not a list but as somethning from a set of things that would work than have it later decide.
    c5s = [] 

    # Get degeneracy ordering in O(n + m)
    # degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

    # TRY OUT EVERY VALID DEGEN ORDERING
    for degeneracy_ordering in permutations([0, 1, 2, 3, 4]):
        c5s = [] 

        # Get later neighbors in O(n + m)
        later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

        # Make new edge_set where each edge u, v is ordered so that v is a later neighbor of u
        # First get the node --> degen index list
        degen_indices = [-1] * graph.number_of_nodes()
        for degen_index, node in enumerate(degeneracy_ordering):
            degen_indices[node] = degen_index

        forward_edges = set()
        for u, v in graph.edges():
            u_d_index = degen_indices[u]
            v_d_index = degen_indices[v]

            if u_d_index < v_d_index: # If v is a later neighbor of u
                forward_edges.add((u, v))
            else:
                forward_edges.add((v, u))


        # print(f"forward edges:")
        # pprint(forward_edges)

        # print(f"later neighbors:")
        # pprint(later_neighbors)

        print(f"degen ordering:")
        pprint(degeneracy_ordering)


        # Do both the later neighbors of the first node have neighbors? --> type 1, else type 2
        type1 = True
        for ln in later_neighbors[degeneracy_ordering[0]]: 
            if len(later_neighbors[ln]) == 0: type1 = False
        if type1: print("type 1")
        else: print("type 2")

        # Look for c5s type 1.2
        for u, v in forward_edges: # O(m)
            """
            Assume that u, v is an edge where a later neighbor of v, named y, is the last in of the c5 in the ordering
            """

            for y in later_neighbors[v]: # O(d)
                # Now we have that u --> v --> y
                # Now we look for u --> w --> x where (x, y) in edges

                for w in later_neighbors[u]: #O(d)
                    if w == v: continue # skip if w == v

                    for x in later_neighbors[w]: #(d)
                        if (x, y) in forward_edges:
                            c5s.append(list([u, v, y, w, x]))

        # Look for c5s type 2.2
        for u, v in forward_edges: # O(m)
            """
            Assume that u->v, is an edge where u has one other later neighbor, named y, the last of the c5 in the ordering
            """
            for y in later_neighbors[u]:
                # Now we have that u -> y, and u -> v
                # We need to find w, x such that v -> w -> x -> y

                for w in later_neighbors[v]:
                    for x in later_neighbors[w]:
                        if (x, y) in forward_edges:
                            c5s.append(list([u, v, y, w, x]))





            # # print(f"1 u={u}, v={v}")
            # # we know that v is a later neighbor of u

            # # Look at all u --> v --> w
            # for w in later_neighbors[v]: # O(d) --> O(md)
            #     # print(f"2 {u}, {v}, w={w}")
            #     if (u, w) in forward_edges: continue # then u --> v --> w is a cycle so skip to next w

            #     for x in later_neighbors[w]: # O(d) --> O(md^2)
            #         # print(f"3 {u}, {v}, {w}, x={x}")
            #         if (u, x) in forward_edges: 
            #             # print(f"not a cycle! {u, x} is a chord")
            #             continue # then u --> v --> w --> x is a cycle so skip to next x
            #         if (v, x) in forward_edges:
            #             # print(f"not a cycle! {v, x} is a chord")
            #             continue # v --> w --> x is a cycle??
            #         # assume that u --> v --> w --> x
            #         # Is there a y?

            #         for y in later_neighbors[x]:  # ≤ d
            #             if y == u or y == v or y == w:
            #                 continue
            #             # Check closure
            #             if (y, u) in forward_edges or (u, y) in forward_edges:
            #                 cycle = tuple(sorted([u, v, w, x, y]))
            #                 c5s.append(cycle)

                    
                    




                    # for y in later_neighbors[x]: # O(d) --> O(md^3)
                    #     print(f"4 {u}, {v}, {w}, {x}, y={y}")
                    #     if (u, y) in forward_edges: # then this is a cycle if no chords from y to v or w
                    #         if (v, y) in forward_edges: 
                    #             print(f"not a cycle! {v, y} is a chord")
                    #             continue
                    #         if (w, y) in forward_edges: 
                    #             print(f"not a cycle! {w, y} is a chord")
                    #             continue

                    #         print("found!")

                    #         c5s.append(set([u, v, w, x, y]))

        print(f"C5s= {c5s} \n")
    return c5s


