from src.algorithms.degeneracy import get_degeneracy, compute_later_neighbors
from src.graph import Graph

# Brute force approach
def find_c5s_slow(G : Graph):
    """
    Brutish Search for c5s: Runs in O(n * highest_degree^4)
    """
    c5s = set()
    
    for v1 in G.nodes():                               # O(n)      -> O(n)            
        for v2 in G.neighbors(v1):                     # O(\delta) -> O(n\delta)
            for v3 in G.neighbors(v2):                 # O(\delta) -> O(n\delta^2)
                if v3 in (v1, v2): continue
                if G.has_edge(v3, v1): continue

                for v4 in G.neighbors(v3):             # O(\delta) -> O(n\delta^3)
                    if v4 in (v1, v2, v3): continue

                    if G.has_edge(v1, v4): continue
                    if G.has_edge(v2, v4): continue

                    for v5 in G.neighbors(v4):         # O(\delta) -> O(n\delta^4)
                        if v5 in (v1, v2, v3, v4): continue
                        # Check if it closes the cycle
                        if G.has_edge(v5, v1):
                            
                            # Make sure no chords
                            if G.has_edge(v5, v2): continue
                            if G.has_edge(v5, v3): continue


                            nodes = set([v1, v2, v3, v4, v5])
                            # if len(nodes) == 5:  # all distinct
                            #     sub = G.subgraph(nodes)
                            #     if sub.number_of_edges() == 5:
                            c5s.add(tuple(sorted(nodes)))
    return list(c5s)

from src.algorithms.degeneracy import get_degeneracy
from pprint import pprint
from itertools import permutations
from collections import defaultdict

# --- WEEK 3 --- #

def get_forward_edges(graph, degeneracy_index_lookup):
    forward_edges = set()
    for u, v in graph.edges():
        u_d_index = degeneracy_index_lookup[u]
        v_d_index = degeneracy_index_lookup[v]

        if u_d_index < v_d_index: # If v is a later neighbor of u
            forward_edges.add((u, v))
        else:
            forward_edges.add((v, u))
    return forward_edges

def get_degeneracy_index_lookup(degeneracy_ordering):
    degen_indices = [-1] * len(degeneracy_ordering)
    for degen_index, node in enumerate(degeneracy_ordering):
        degen_indices[node] = degen_index
    return degen_indices


def degeneracy_c5_search(graph: Graph, remove_degree_one_vertices = True):
    # If removing degree_one_vertices
    if remove_degree_one_vertices: graph = remove_degree_1_vertices(graph)

    # Get degeneracy ordering in O(n + m)
    degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

    # Get degeneracy index lookup in O(n)
    degeneracy_indices = get_degeneracy_index_lookup(degeneracy_ordering)

    # Get forward edge list in O(m)
    forward_edges = get_forward_edges(graph, degeneracy_indices)

    # Get forward edge lookup set
    forward_edges_set = set(forward_edges)

    # Compute later neighbors in O(n + m)
    later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

    # Initialize resulting set
    c5s = set()

    # For each edge, look if u, v is a part of a c5 where u is the first from the c5 in the degeneracy ordering
    for u, v in forward_edges:
        if (u, v) == (18, 0): print("got the edge")

        # Type ONE: u -> v -> x -> w -> y, u -> y
        c5s = find_c5_type_one(u, v, forward_edges_set, later_neighbors, c5s)


        # Type TWO: u -> v -> x -> w, u -> y -> w       (do I need to check if it could be w -> x?)
        c5s = find_c5_type_two(u, v, forward_edges_set, later_neighbors, c5s)

        # Type THREE: u -> v -> x, u -> y, w -> x, w -> y
        # Type FOUR: u -> v, u -> y, x -> v, x -> w -> y
        c5s = find_c5_type_three_and_four(u, v, forward_edges_set, later_neighbors, graph, c5s)
        
    return c5s

def find_c5_type_one(u, v, forward_edges_set, later_neighbors, c5s):
    for x in later_neighbors[v]: # O(md)
            if (u, x) in forward_edges_set: continue # Don't allow u-x

            for w in later_neighbors[x]: # O(md^2)
                if (u, w) in forward_edges_set: continue # Don't allow u-w
                if (v, w) in forward_edges_set: continue # Don't allow v-w

                for y in later_neighbors[w]: #O(md^3)
                    if (v, y) in forward_edges_set: continue
                    if (x, y) in forward_edges_set: continue

                    if (u, y) in forward_edges_set:
                        c5s.add((u, v, x, w, y))
    return c5s

def find_c5_type_two(u, v, forward_edges_set, later_neighbors, c5s):
    for x in later_neighbors[v]: # O(md)
        if (u, x) in forward_edges_set: continue # Don't allow u-x

        for w in later_neighbors[x]: # O(md^2)
            if (u, w) in forward_edges_set: continue # Don't allow u-w
            if (v, w) in forward_edges_set: continue # Don't allow v-w

            for y in later_neighbors[u]: # O(md^3)
                if (v, y) in forward_edges_set: continue
                if (y, v) in forward_edges_set: continue
                if (x, y) in forward_edges_set: continue
                if (y, x) in forward_edges_set: continue

                if (y, w) in forward_edges_set:
                    c5s.add((u, v, x, w, y))
    return c5s

def find_c5_type_three_and_four(u, v, forward_edges_set, later_neighbors, graph, c5s):
    for x in later_neighbors[v]: # O(md)
        if (u, x) in forward_edges_set: continue # Don't allow u-x

        for y in later_neighbors[u]: # O(md^2)
            if (v, y) in forward_edges_set: continue
            if (y, v) in forward_edges_set: continue
            if (x, y) in forward_edges_set: continue
            if (y, x) in forward_edges_set: continue

            for w in graph.neighbors(x): #O(md^2 delta)
                if (x, w) in forward_edges_set: continue
                if graph.has_edge(u, w): continue
                if graph.has_edge(w, v): continue

                # if (w, x) in forward_edges_set:
                if (w, y) in forward_edges_set:
                    c5s.add((u, v, x, w, y))
    return c5s

def remove_degree_1_vertices_slow(graph_obj: Graph):
    """
    Repeatedly removes all degree-1 vertices from a NetworkX graph
    until no such vertices remain (computes the 2-core).
    Operates in-place and also returns the graph.
    """
    graph = graph_obj.nx_graph()

    # Use a queue to avoid scanning all nodes repeatedly
    deg1_nodes = [node for node, deg in graph.degree if deg == 1]
    
    while deg1_nodes:
        graph.remove_nodes_from(deg1_nodes)
        # Update candidates: neighbors might now have degree 1
        deg1_nodes = [node for node, deg in graph.degree if deg == 1]
    

    edge_list = graph.edges()

    return Graph(edge_list, name=graph_obj.name)


from src.bucket_queue import BucketQueue

def remove_degree_1_vertices(graph : Graph):
    n = graph.number_of_nodes()
    if n == 0:
        return graph

    # Initialize degree dictionary
    degree = {u: graph.degree(u) for u in graph.nodes()}
    max_deg = max(degree.values(), default=0)

    # Initialize bucket queue with vertices by degree
    bq = BucketQueue(max_deg)
    for u, deg in degree.items():
        bq.push(deg, u)

    removed = [False] * graph.number_of_nodes()

    while not bq.is_empty():
        v = bq.pop_min()
        if v is None or removed[v]:
            continue

        if degree[v] <= 1:
            removed[v] = True
            # Remove v from the graph
            for u in list(graph.neighbors(v)):
                if not removed[u]:
                    # Decrease neighbor’s degree
                    degree[u] -= 1
                    bq.push(degree[u], u)

    new_edge_list = []
    for u, v in graph.edges():
        if removed[u] or removed[v]: continue
        new_edge_list.append((u, v))

    return Graph(new_edge_list, graph.name)




'''
def degeneracy_c5_search(graph: Graph):
    # Get degeneracy ordering in O(n + m)
    degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

    # Get degeneracy index lookup in O(n)
    degeneracy_indices = get_degeneracy_index_lookup(degeneracy_ordering)

    # Get forward edge list in O(m)
    forward_edges = get_forward_edges(graph, degeneracy_indices)

    # Get forward edge lookup set
    forward_edges_set = set(forward_edges)

    # Compute later neighbors in O(n + m)
    later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

    # Initialize resulting set
    c5s = set()

    # For each edge, look if u, v is a part of a c5 where u is the first from the c5 in the degeneracy ordering
    for u, v in forward_edges:
        if (u, v) == (18, 0): print("got the edge")

        # Type ONE: u -> v -> x -> w -> y, u -> y


        for x in later_neighbors[v]: # O(md)
            if (u, x) in forward_edges_set: continue # Don't allow u-x

            for w in later_neighbors[x]: # O(md^2)
                if (u, w) in forward_edges_set: continue # Don't allow u-w
                if (v, w) in forward_edges_set: continue # Don't allow v-w

                for y in later_neighbors[w]: #O(md^3)
                    if (v, y) in forward_edges_set: continue
                    if (x, y) in forward_edges_set: continue

                    if (u, y) in forward_edges_set:
                        c5s.add((u, v, x, w, y))
        
        # if c5_found: continue

        # Type TWO: u -> v -> x -> w, u -> y -> w       (do I need to check if it could be w -> x?)

        for x in later_neighbors[v]: # O(md)
            if (u, x) in forward_edges_set: continue # Don't allow u-x

            for w in later_neighbors[x]: # O(md^2)
                if (u, w) in forward_edges_set: continue # Don't allow u-w
                if (v, w) in forward_edges_set: continue # Don't allow v-w

                for y in later_neighbors[u]: # O(md^3)
                    if (v, y) in forward_edges_set: continue
                    if (y, v) in forward_edges_set: continue
                    if (x, y) in forward_edges_set: continue
                    if (y, x) in forward_edges_set: continue

                    if (y, w) in forward_edges_set:
                        c5s.add((u, v, x, w, y))
        
        # if c5_found: continue

        # Type THREE: u -> v -> x, u -> y, w -> x, w -> y
        # Type FOUR: u -> v, u -> y, x -> v, x -> w -> y
        for x in later_neighbors[v]: # O(md)
            if (u, x) in forward_edges_set: continue # Don't allow u-x

            for y in later_neighbors[u]: # O(md^2)
                if (v, y) in forward_edges_set: continue
                if (y, v) in forward_edges_set: continue
                if (x, y) in forward_edges_set: continue
                if (y, x) in forward_edges_set: continue

                u_index = degeneracy_indices[u]
                for w in graph.neighbors(x): #O(md^2n)
                    if (x, w) in forward_edges_set: continue
                    if graph.has_edge(u, w): continue
                    if graph.has_edge(w, v): continue

                    # if (w, x) in forward_edges_set:
                    if (w, y) in forward_edges_set:
                        c5s.add((u, v, x, w, y))


        # # Type FOUR: u -> v, u -> y, x -> v, x -> w -> y
        # for y in later_neighbors[u]: # O(md)
        #     if (v, y) in forward_edges_set: continue # Don't allow v-y
        #     if (y, v) in forward_edges_set: continue # Don't allow y-v

        #     u_index = degeneracy_indices[u]
        #     # for x in degeneracy_ordering[u_index:]: #O(mdn)
        #     for x in graph.neighbors(v):
        #         if graph.has_edge(u, x): continue
        #         if graph.has_edge(x, y): continue

        #         # if graph.has_edge(x, v):
        #         for w in later_neighbors[x]:
        #             if graph.has_edge(w, u): continue
        #             if graph.has_edge(w, v): continue

        #             if (w, y) in forward_edges_set:
        #                 c5s.add((u, v, x, w, y))


    return c5s
'''


'''
def degeneracy_c5_search(graph: Graph):
    # Get degeneracy ordering in O(n + m)
    degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

    for degeneracy_ordering in permutations(list(range(0, len(graph.nodes())))):

        # Get degeneracy index lookup in O(n)
        degeneracy_indices = get_degeneracy_index_lookup(degeneracy_ordering)

        # Get forward edge list in O(m)
        forward_edges = get_forward_edges(graph, degeneracy_indices)

        # Get forward edge lookup set
        forward_edges_set = set(forward_edges)

        # Compute later neighbors in O(n + m)
        later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

        # Initialize resulting set
        c5s = set()

        # For each edge, look if u, v is a part of a c5 where u is the first from the c5 in the degeneracy ordering
        for u, v in forward_edges:
            c5_found = False

            # Type ONE: u -> v -> x -> w -> y, u -> y
            for x in later_neighbors[v]: # O(md)
                if (u, x) in forward_edges_set: continue # Don't allow u-x

                for w in later_neighbors[x]: # O(md^2)
                    if (u, w) in forward_edges_set: continue # Don't allow u-w
                    if (v, w) in forward_edges_set: continue # Don't allow v-w

                    for y in later_neighbors[w]: #O(md^3)
                        if (v, y) in forward_edges_set: continue
                        if (x, y) in forward_edges_set: continue

                        if (u, y) in forward_edges_set:
                            c5s.add((u, v, x, w, y))
                            c5_found = True
            
            if c5_found: continue

            # Type TWO: u -> v -> x -> w, u -> y -> w       (do I need to check if it could be w -> x?)

            for x in later_neighbors[v]: # O(md)
                if (u, x) in forward_edges_set: continue # Don't allow u-x

                for w in later_neighbors[x]: # O(md^2)
                    if (u, w) in forward_edges_set: continue # Don't allow u-w
                    if (v, w) in forward_edges_set: continue # Don't allow v-w

                    for y in later_neighbors[u]: # O(md^3)
                        if (v, y) in forward_edges_set: continue
                        if (y, v) in forward_edges_set: continue
                        if (x, y) in forward_edges_set: continue
                        if (y, x) in forward_edges_set: continue

                        if (y, w) in forward_edges_set:
                            c5s.add((u, v, x, w, y))
                            c5_found = True
            
            if c5_found: continue

            # Type THREE: u -> v -> x, u -> y, w -> x, w -> y
            for x in later_neighbors[v]: # O(md)
                if (u, x) in forward_edges_set: continue # Don't allow u-x

                for y in later_neighbors[u]: # O(md^2)
                    if (v, y) in forward_edges_set: continue
                    if (y, v) in forward_edges_set: continue
                    if (x, y) in forward_edges_set: continue
                    if (y, x) in forward_edges_set: continue

                    u_index = degeneracy_indices[u]
                    for w in degeneracy_ordering[u_index:]: #O(md^2n)
                        if graph.has_edge(u, w): continue
                        if graph.has_edge(w, v): continue

                        if (w, x) in forward_edges_set:
                            if (w, y) in forward_edges_set:
                                c5s.add((u, v, x, w, y))
                                c5_found = True
            
            if c5_found: continue

            # Type FOUR: u -> v, u -> y, x -> v, x -> w -> y
            for y in later_neighbors[u]: # O(md)
                if (v, y) in forward_edges_set: continue # Don't allow v-y
                if (y, v) in forward_edges_set: continue # Don't allow y-v

                u_index = degeneracy_indices[u]
                for x in degeneracy_ordering[u_index:]: #O(mdn)
                    if graph.has_edge(u, x): continue
                    if graph.has_edge(x, y): continue

                    if graph.has_edge(x, v):
                        for w in later_neighbors[x]:
                            if graph.has_edge(w, u): continue
                            if graph.has_edge(w, v): continue

                            if (w, y) in forward_edges_set:
                                c5s.add((u, v, x, w, y))


        if len(c5s) != 2: print(f"DEGEN_ORDERING = {degeneracy_ordering}\nNUMBER = {len(c5s)}")    






    return c5s



'''







        
















# --- WEEK 2 --- #

# # def degeneracy_c5_search(graph : Graph):
# #     # I want to define this as not a list but as somethning from a set of things that would work than have it later decide.
# #     c5s = [] 

# #     # Get degeneracy ordering in O(n + m)
# #     # degeneracy_ordering, graph_degeneracy = get_degeneracy(graph)

# #     # TRY OUT EVERY VALID DEGEN ORDERING
# #     for degeneracy_ordering in permutations([0, 1, 2, 3, 4]):
# #         c5s = [] 

# #         # Get later neighbors in O(n + m)
# #         later_neighbors = compute_later_neighbors(graph, degeneracy_ordering)

# #         # Make new edge_set where each edge u, v is ordered so that v is a later neighbor of u
# #         # First get the node --> degen index list
# #         degen_indices = [-1] * graph.number_of_nodes()
# #         for degen_index, node in enumerate(degeneracy_ordering):
# #             degen_indices[node] = degen_index

# #         forward_edges = set()
# #         for u, v in graph.edges():
# #             u_d_index = degen_indices[u]
# #             v_d_index = degen_indices[v]

# #             if u_d_index < v_d_index: # If v is a later neighbor of u
# #                 forward_edges.add((u, v))
# #             else:
# #                 forward_edges.add((v, u))


# #         # print(f"forward edges:")
# #         # pprint(forward_edges)

# #         # print(f"later neighbors:")
# #         # pprint(later_neighbors)

# #         print(f"degen ordering:")
# #         pprint(degeneracy_ordering)


# #         # Does zero have later neighbors with neighbors? --> type 1, else type 2
# #         type1 = True
# #         for ln in later_neighbors[0]: 
# #             if len(later_neighbors[ln]) == 0: type1 = False
# #         if type1: print("type 1")
# #         else: print("type 2")

# #         # Look for c5s
# #         for u, v in forward_edges: # O(m)
# #             # print(f"1 u={u}, v={v}")
# #             # we know that v is a later neighbor of u

# #             # Look at all u --> v --> w
# #             for w in later_neighbors[v]: # O(d) --> O(md)
# #                 # print(f"2 {u}, {v}, w={w}")
# #                 if (u, w) in forward_edges: continue # then u --> v --> w is a cycle so skip to next w

# #                 for x in later_neighbors[w]: # O(d) --> O(md^2)
# #                     # print(f"3 {u}, {v}, {w}, x={x}")
# #                     if (u, x) in forward_edges: 
# #                         # print(f"not a cycle! {u, x} is a chord")
# #                         continue # then u --> v --> w --> x is a cycle so skip to next x
# #                     if (v, x) in forward_edges:
# #                         # print(f"not a cycle! {v, x} is a chord")
# #                         continue # v --> w --> x is a cycle??
# #                     # assume that u --> v --> w --> x
# #                     # Is there a y?

# #                     for y in later_neighbors[x]:  # ≤ d
# #                         if y == u or y == v or y == w:
# #                             continue
# #                         # Check closure
# #                         if (y, u) in forward_edges or (u, y) in forward_edges:
# #                             cycle = tuple(sorted([u, v, w, x, y]))
# #                             c5s.append(cycle)

                    
                    




# #                     # for y in later_neighbors[x]: # O(d) --> O(md^3)
# #                     #     print(f"4 {u}, {v}, {w}, {x}, y={y}")
# #                     #     if (u, y) in forward_edges: # then this is a cycle if no chords from y to v or w
# #                     #         if (v, y) in forward_edges: 
# #                     #             print(f"not a cycle! {v, y} is a chord")
# #                     #             continue
# #                     #         if (w, y) in forward_edges: 
# #                     #             print(f"not a cycle! {w, y} is a chord")
# #                     #             continue

# #                     #         print("found!")

# #                     #         c5s.append(set([u, v, w, x, y]))

# #         print(f"C5s= {c5s} \n")
# #     return c5s


# # Only meant to account for type 1.2
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


#         # Do both the later neighbors of the first node have neighbors? --> type 1, else type 2
#         type1 = True
#         for ln in later_neighbors[degeneracy_ordering[0]]: 
#             if len(later_neighbors[ln]) == 0: type1 = False
#         if type1: print("type 1")
#         else: print("type 2")

#         # Look for c5s type 1.2
#         for u, v in forward_edges: # O(m)
#             """
#             Assume that u, v is an edge where a later neighbor of v, named y, is the last in of the c5 in the ordering
#             """

#             for y in later_neighbors[v]: # O(d)
#                 # Now we have that u --> v --> y
#                 # Now we look for u --> w --> x where (x, y) in edges

#                 for w in later_neighbors[u]: #O(d)
#                     if w == v: continue # skip if w == v

#                     for x in later_neighbors[w]: #(d)
#                         if (x, y) in forward_edges:
#                             c5s.append(list([u, v, y, w, x]))

#         # Look for c5s type 2.2
#         for u, v in forward_edges: # O(m)
#             """
#             Assume that u->v, is an edge where u has one other later neighbor, named y, the last of the c5 in the ordering
#             """
#             for y in later_neighbors[u]:
#                 # Now we have that u -> y, and u -> v
#                 # We need to find w, x such that v -> w -> x -> y

#                 for w in later_neighbors[v]:
#                     for x in later_neighbors[w]:
#                         if (x, y) in forward_edges:
#                             c5s.append(list([u, v, y, w, x]))





#             # # print(f"1 u={u}, v={v}")
#             # # we know that v is a later neighbor of u

#             # # Look at all u --> v --> w
#             # for w in later_neighbors[v]: # O(d) --> O(md)
#             #     # print(f"2 {u}, {v}, w={w}")
#             #     if (u, w) in forward_edges: continue # then u --> v --> w is a cycle so skip to next w

#             #     for x in later_neighbors[w]: # O(d) --> O(md^2)
#             #         # print(f"3 {u}, {v}, {w}, x={x}")
#             #         if (u, x) in forward_edges: 
#             #             # print(f"not a cycle! {u, x} is a chord")
#             #             continue # then u --> v --> w --> x is a cycle so skip to next x
#             #         if (v, x) in forward_edges:
#             #             # print(f"not a cycle! {v, x} is a chord")
#             #             continue # v --> w --> x is a cycle??
#             #         # assume that u --> v --> w --> x
#             #         # Is there a y?

#             #         for y in later_neighbors[x]:  # ≤ d
#             #             if y == u or y == v or y == w:
#             #                 continue
#             #             # Check closure
#             #             if (y, u) in forward_edges or (u, y) in forward_edges:
#             #                 cycle = tuple(sorted([u, v, w, x, y]))
#             #                 c5s.append(cycle)

                    
                    




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


