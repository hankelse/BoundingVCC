from src.algorithms.c5_search import degeneracy_c5_search
from src.structures.graph import Graph

from src.solvers.tools.reductions import apply_reductions_external, removed_masked_nodes

from src.solvers.tools.subgraph_heuristics import smallest_neighborhood, largest_neighborhood, closed_neighborhood
from src.solvers.tools.evaluate_subgraph import trivial_neighborhood_bound
from src.solvers.tools.external_solvers import find_indepedent_set_size

from src.solvers.frameworks.reduce_and_act import ReduceAndAct



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
    
