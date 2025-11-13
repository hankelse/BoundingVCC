from src.algorithms.c5_search import degeneracy_c5_search
from src.structures.graph import Graph

from src.algorithms.reductions import apply_reductions_external, removed_masked_nodes

from src.solvers.tools.subgraph_heuristics import smallest_neighborhood, largest_neighborhood, closed_neighborhood
from src.solvers.tools.evaluate_subgraph import trivial_neighborhood_bound
from src.solvers.tools.external_solvers import find_indepedent_set_size

from src.solvers.frameworks.reduce_and_act import ReduceAndAct

# def reduce_and_bound(graph: Graph, 
#                      reductions=apply_reductions_external,
#                      heuristic=smallest_neighborhood, 
#                      neighborhood_bound=trivial_neighborhood_bound, 
#                      auxiliary_bounder=find_indepedent_set_size,
#                      clique_cover=None, 
#                      offset = 0):
#     algo = ReduceAndBound(reductions=reductions,
#                           pat_finder= degeneracy_c5_search,
#                           pat_choice_heuristic=heuristic,
#                           pat_neighborhood_evaluator=neighborhood_bound,
#                           auxiliary_solver=auxiliary_bounder,
#                           clique_cover=clique_cover)
#     return algo.run(graph)

def reduce_and_bound(graph: Graph, **kwargs):
    """Convenience wrapper to run the Reduce-and-Bound algorithm."""
    return ReduceAndBound(**kwargs).run(graph)

class ReduceAndBound(ReduceAndAct):
    """
    Reduce-and-Bound paradigm:
    - Applies reductions
    - Finds C5 patterns (or others)
    - Removes their closed neighborhoods
    - Accumulates a bound increment via a neighborhood bound function
    - Finalizes with an auxiliary solver
    """

    def __init__(self,
                 reductions,
                 pat_finder,
                 pat_choice_heuristic,
                 pat_neighborhood_evaluator,
                 auxiliary_solver,
                 clique_cover=None):
        super().__init__(reductions,
                         pat_finder,
                         pat_choice_heuristic,
                         pat_neighborhood_evaluator,
                         auxiliary_solver)
        self.pat_neighborhood_evaluator = pat_neighborhood_evaluator
        self.clique_cover = clique_cover or []

    # === Subclass-specific behavior ===

    def act_on_pattern_neighborhood(self, graph, chosen_neighborhood):
        """
        Removes the chosen neighborhood and adds to the accumulated bound.
        Returns (next_graph, delta_value).
        """
        # Remove nodes in the chosen neighborhood
        removal_mask = [False] * graph.number_of_nodes()
        for node in chosen_neighborhood:
            removal_mask[node] = True

        # Compute the contribution to the bound
        delta_value = self.neighborhood_bound_func(graph, chosen_neighborhood)
        print(f"Removing neighborhood of size {len(chosen_neighborhood)}; "
              f"Δbound = {delta_value}")

        # Remove from graph
        next_graph = removed_masked_nodes(graph, removal_mask)
        return next_graph, delta_value

    def finalize(self, graph, accumulated_value):
        """
        Runs the auxiliary solver when no more patterns exist.
        """
        remaining_bound = self.auxiliary_solver(graph)
        total_bound = accumulated_value + remaining_bound + len(self.clique_cover)

        return total_bound
    



# OLD
# def reduce_and_bound(graph: Graph, 
#                      reductions=apply_reductions_external,
#                      heuristic=smallest_neighborhood, 
#                      neighborhood_bound=trivial_neighborhood_bound, 
#                      auxiliary_bounder=find_indepedent_set_size,
#                      clique_cover=None, 
#                      offset = 0):
    
#     if clique_cover == None: clique_cover = []
    
#     '''
#     Takes a graph and applies data reductions until it can't anymore.
#     Then, uses an heuristic h, to choose a c5 in the graph to remove
#     Then, removes N[c5] and increments an offset by 3
#     Then, repeats until there is no more c5 and no more reductions
#     '''

#     # 1) ======== DATA REDUCTIONS ===== #
#     masked_nodes, cliques = reductions(graph)
#     reduced = removed_masked_nodes(graph, masked_nodes)
#     clique_cover += cliques

#     if reduced.number_of_edges() >= 5: # If there can be a c5
#         print(f"Applied Reductions: {graph.number_of_nodes()} --> {reduced.number_of_nodes()}, found {len(cliques)} cliques.")

#         # 2) ======== C5 SEARCH ===== #
#         c5s = degeneracy_c5_search(reduced)
#         print(f"Preformed c5 search: {len(c5s)} c5s.")

#     else:
#         c5s = []

#     # 3) ======= CHECK BASE CASE ====== #
#     found_c5s = len(c5s) != 0
#     if found_c5s:

#         # 4) ======= GET N[C5s] ====== #
#         c5s = list(c5s) # Wrap in a list for iterating over and storing indices
#         c5_neighborhoods = []
#         for c5 in c5s:
#             c5_neighborhoods.append(closed_neighborhood(c5, reduced))
#         print(f"Expanded c5s to N[c5s]")

#         # 5) ======= REMOVE A C5 ====== #
#         chosen = heuristic(reduced, c5_neighborhoods)
#         neighborhood_removal_mask = [False] * reduced.number_of_nodes()
#         for node in chosen:
#             neighborhood_removal_mask[node] = True
#         offset += neighborhood_bound(reduced, chosen)
#         print(f"just got an offset of neighborhood of: ", neighborhood_bound(reduced, chosen))
#         next_graph = removed_masked_nodes(reduced, neighborhood_removal_mask)

#         # 6) ======= RECUR ===== #

#         return reduce_and_bound(next_graph, reductions=reductions, heuristic=heuristic, neighborhood_bound=neighborhood_bound, clique_cover=clique_cover, auxiliary_bounder=auxiliary_bounder, offset=offset)
    
#     else: # No c5s found --> Run Auxilary Bounder

#         # 7) ======= RUN auxilary bounder ===== #
#         lower_bound_remaining_graph = auxiliary_bounder(reduced)
#         bound = lower_bound_remaining_graph + offset + len(clique_cover)
#         return bound
    
