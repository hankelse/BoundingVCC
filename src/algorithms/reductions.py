

from src.graph import Graph

from collections import deque

def apply_reductions(graph: Graph, removed_nodes=None):
    """
    Applies exhausted reductions on given graph,
    Returns 
        a lookup array of removed nodes 
        the removed cliques
    """

    if removed_nodes == None: removed_nodes = [False]*graph.number_of_nodes()
    # print(len(removed_nodes))
    clique_cover = []

    new_cliques, removed_nodes = n_degree_isolated_vertex(graph, 2, removed_nodes)
    while new_cliques != []:
        clique_cover += new_cliques
        new_cliques, removed_nodes = n_degree_isolated_vertex(graph, 2, removed_nodes)
        
    
    return removed_nodes, clique_cover


def removed_masked_nodes(graph : Graph, removed_nodes):
    new_edge_list = []
    edges = graph.edges()

    for u, v in edges:
        if removed_nodes[u]: continue
        if removed_nodes[v]: continue
        new_edge_list.append((u, v))
    
    return Graph(new_edge_list)







def n_degree_isolated_vertex(graph : Graph, n, removed):
    # Preforms 1 pass of the isolated vertex rule only checking nodes of degree >= n
    cliques = []

    for node in graph.nodes():
        # print(graph.number_of_nodes(), len(removed))
        # print(node)
        if removed[node]: continue # Skip if node is removed

        degree = graph.degree(node)

        # Skip nodes of higher degree than n
        if degree > n: continue
        
        # Check if neighborhood forms a clique
        if (is_clique(graph, graph.neighbors(node), removed)):

            # Add clique to cover
            clique = graph.neighbors(node) + [node]
            cliques.append(clique)

            # set all nodes as removed
            for node in clique:
                removed[node] = True
    
    return cliques, removed


                
            







def is_clique(graph : Graph, nodes, removed=None):
    if removed == None: removed = [False]*graph.number_of_nodes()

    n = len(nodes)
    if n < 2:
        return True  # 0- or 1-node set is trivially a clique

    # direct neighbor lookup from the underlying adjacency dictionary
    adj = graph._graph._adj  

    for i in range(n):
        u = nodes[i]
        if removed[u]: continue
        # if u not in adj:
        #     return False
        
        neighbors_u = adj[u]
        # All later nodes must be neighbors of u
        for j in range(i + 1, n):
            v = nodes[j]
            if removed[v]: continue

            if v not in neighbors_u:
                return False

    return True









# def exhaust_inplace(reduction_callers):
#     """
#     Optimized version of 'exhaust' that performs all reductions in-place.
#     It keeps track of active nodes and avoids operating on removed ones.
#     """

#     if not isinstance(reduction_callers, list):
#         reduction_callers = [reduction_callers]

#     def run(G: Graph):
#         lifters = []
#         active = set(G.nodes())              # current set of nodes
#         queue = deque(active)                # vertices to check

#         while queue:
#             v = queue.popleft()

#             # Skip if v was removed by a previous reduction
#             if v not in active:
#                 continue

#             for reduction in reduction_callers:
#                 reduced, lifter, affected = reduction(G, v)

#                 if lifter is not None:
#                     lifters.append(lifter)

#                     # Update active set (some vertices may be gone)
#                     active = set(G.nodes())

#                     # Add affected neighbors to queue (if still alive)
#                     for n in affected:
#                         if n in active:
#                             queue.append(n)

#                     # Once one reduction applies, skip the rest for this vertex
#                     break

#         return G, lifters

#     run.is_rule_caller = True
#     return run


# def is_neighborhood_clique_fast(G: Graph, v: int) -> bool:
#     """
#     Fast check: neighborhood is a clique if induced edges = deg*(deg-1)/2
#     """
#     neigh = G.neighbors(v)
#     n = len(neigh)
#     if n < 2:
#         return True
#     # NetworkX subgraph is efficient for small induced sets
#     sub_e = G._graph.subgraph(neigh).number_of_edges()
#     return sub_e == n * (n - 1) // 2


# def isolated_vertex(G: Graph, v: int):
#     """
#     If N(v) forms a clique, v ∈ every MIS.
#     Remove v ∪ N(v) and return lifter + affected neighbors.
#     """
#     if v not in G._graph:
#         return G, None, set()

#     if not is_neighborhood_clique_fast(G, v):
#         return G, None, set()

#     # Collect nodes to remove
#     to_remove = set(G.neighbors(v)) | {v}
#     affected = set()
#     for u in to_remove:
#         affected.update(G.neighbors(u))
#     affected -= to_remove  # skip removed vertices

#     for u in to_remove:
#         if u in G._graph:
#             G.remove_node(u)

#     def add_isolated_vertex(solution: set[int]) -> set[int]:
#         solution.add(v)
#         return solution

#     return G, add_isolated_vertex, affected


# def vertex_fold(G: Graph, v: int):
#     """
#     If v has deg=2 and its neighbors u,w are not adjacent,
#     fold {u,v,w} into v.
#     """
#     if v not in G._graph or G.degree(v) != 2:
#         return G, None, set()

#     u, w = G.neighbors(v)
#     if G.has_edge(u, w):
#         return G, None, set()

#     # Add u and w’s neighbors to v
#     for n in G.neighbors(u):
#         if n != v:
#             G.add_edge(v, n)
#     for n in G.neighbors(w):
#         if n != v:
#             G.add_edge(v, n)

#     # Track affected vertices (neighbors of u, w, v)
#     affected = set(G.neighbors(v)) | {v}

#     # Remove u, w
#     if u in G._graph:
#         G.remove_node(u)
#     if w in G._graph:
#         G.remove_node(w)

#     def undo_fold(solution: set[int]) -> set[int]:
#         if v not in solution:
#             solution.add(v)
#         else:
#             solution.remove(v)
#             solution.update({u, w})
#         return solution

#     return G, undo_fold, affected


# # ===== CALLING REDUCTIONS ==== #

# def apply_reductions(G: Graph):

#     reduced, lifters = exhaust([isolated_vertex, vertex_fold])(G)

#     return reduced, lifters


# def exhaust(reduction_callers):
#     """
#     Given one or more reduction functions, returns a callable that repeatedly
#     applies them to a Graph until no further reductions are possible.

#     Each reduction must follow the convention:
#         reduction(G: Graph) -> (Graph, lifter or None)

#     The returned function:
#         - Takes a Graph
#         - Returns a reduced Graph and a list of lifters
#     """

#     # Normalize to list
#     if not isinstance(reduction_callers, list):
#         reduction_callers = [reduction_callers]

#     def exhaustively_applied(G: Graph):
#         instructions = []
#         current_num_instructions = 0
#         G_red = G.copy()

#         while True:
#             for reduction in reduction_callers:
#                 G_red, new_instruction = reduction(G_red)

#                 # Some reductions return a single callable or None
#                 if new_instruction is None:
#                     continue
#                 elif isinstance(new_instruction, list):
#                     instructions.extend(new_instruction)
#                 else:
#                     instructions.append(new_instruction)

#             # Stop if no new instructions were added in this pass
#             if len(instructions) == current_num_instructions:
#                 break
#             else:
#                 current_num_instructions = len(instructions)

#         return G_red, instructions

#     # Tag to indicate it’s a reduction caller
#     exhaustively_applied.is_rule_caller = True
#     return exhaustively_applied


# # ===== REDUCTIONS ==== #


# def is_neighborhood_clique(G: Graph, v: int) -> bool:
#     """
#     Check whether the open neighborhood of vertex v forms a clique.
#     """
#     neighbors = G.neighbors(v)
#     n = len(neighbors)
#     if n < 2:
#         return True

#     for i in range(n):
#         u = neighbors[i]
#         for j in range(i + 1, n):
#             if not G.has_edge(u, neighbors[j]):
#                 return False
#     return True


# def isolated_vertex(G: Graph):
#     """
#     Reduction 1: Isolated Vertex (neighborhood is a clique)
#     ------------------------------------------------------
#     If a vertex v has a neighborhood that forms a clique,
#     then v must be in every maximum independent set.
#     So remove v and its neighbors from the graph.
#     """
#     for v in G.nodes():
#         if is_neighborhood_clique(G, v):
#             G_copy = G.copy()
#             neighborhood = G.neighbors(v)
#             for node in neighborhood + [v]:
#                 G_copy.remove_node(node)

#             def add_isolated_vertex(solution: set[int]) -> set[int]:
#                 solution.add(v)
#                 return solution

#             return G_copy, add_isolated_vertex

#     return G, None


# def vertex_fold(G: Graph):
#     """
#     Reduction 2: Vertex Folding
#     ----------------------------
#     If a vertex v has degree 2 and its two neighbors u and w are not adjacent,
#     then either v ∈ MIS or both {u, w} ⊆ MIS.
#     Contract {u, v, w} into a single vertex v.
#     """
#     for v in G.nodes():
#         if G.degree(v) == 2:
#             neighbors = G.neighbors(v)
#             u, w = neighbors[0], neighbors[1]
#             if not G.has_edge(u, w):  # Non-adjacent neighbors
#                 G_copy = G.copy()

#                 # Add edges from u and w’s neighbors to v
#                 for u_neighbor in G.neighbors(u):
#                     if u_neighbor != v:
#                         G_copy.add_edge(v, u_neighbor)
#                 for w_neighbor in G.neighbors(w):
#                     if w_neighbor != v:
#                         G_copy.add_edge(v, w_neighbor)

#                 # Remove u and w
#                 G_copy.remove_node(u)
#                 G_copy.remove_node(w)

#                 def undo_fold(solution: set[int]) -> set[int]:
#                     if v not in solution:
#                         solution.add(v)
#                     else:
#                         solution.remove(v)
#                         solution.update({u, w})
#                     return solution

#                 return G_copy, undo_fold

#     return G, None


# def identity(solution: set[int]) -> set[int]:
#     """Identity lifter (no change to solution)."""
#     return solution
