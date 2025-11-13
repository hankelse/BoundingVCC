from src.solvers.frameworks.reduce_and_act import ReduceAndAct
from src.algorithms.reductions import removed_masked_nodes
from src.structures.graph import Graph



def reduce_and_peel(graph: Graph, **kwargs):
    """Convenience wrapper to run the Reduce-and-Peel algorithm."""
    return ReduceAndPeel(**kwargs).run(graph)



from src.solvers.frameworks.reduce_and_act import ReduceAndAct
from src.algorithms.reductions import removed_masked_nodes


class ReduceAndPeel(ReduceAndAct):
    """
    Reduce-and-Peel paradigm:
    - Applies reductions
    - Finds patterns (C5s or otherwise)
    - Peels off N[pattern] with a clique cover of it
    - Tracks the number of cliques returned by these covers
    - Repeats until no patterns remain
    - Finalizes by possibly solving the residual graph and adding its clique count
    """

    def __init__(self,
                 reductions,
                 pat_finder,
                 pat_choice_heuristic,
                 pat_neighborhood_evaluator,
                 auxiliary_solver):
        super().__init__(reductions,
                         pat_finder,
                         pat_choice_heuristic,
                         pat_neighborhood_evaluator,
                         auxiliary_solver)
        # Track total clique count
        self.total_cliques = 0

    def act_on_pattern_neighborhood(self, graph, chosen_neighborhood):
        """
        Removes N[pattern], covers it with a clique cover, and increments
        the total clique count by the number of cliques returned.
        Returns (next_graph, delta_value), where delta_value is the number
        of cliques added in this step.
        """

        # === Step 1: Compute clique cover of N[pattern] ===
        num_covered_cliques = self.pat_neighborhood_evaluator(graph, chosen_neighborhood)
        self.total_cliques += num_covered_cliques

        # === Step 2: Remove N[pattern] from the graph ===
        removal_mask = [False] * graph.number_of_nodes()
        for node in chosen_neighborhood:
            removal_mask[node] = True
        next_graph = removed_masked_nodes(graph, removal_mask)

        print(f"Peeling N[pattern] of size {len(chosen_neighborhood)}; ")
            #   f"found {num_covered_cliques} cliques (total = {self.total_cliques})")

        return next_graph, num_covered_cliques

    def finalize(self, graph, accumulated_value):
        """
        Once no patterns remain, run the auxiliary solver on the remaining graph
        and add its clique count to the total.
        Returns the total number of cliques found overall.
        """
        final_cover = self.auxiliary_solver(graph)
        if isinstance(final_cover, list):
            num_final_cliques = len(final_cover)
        elif isinstance(final_cover, int):
            # Allow numeric return for flexibility
            num_final_cliques = final_cover
        else:
            raise TypeError("Expected auxiliary_solver to return list or int")

        self.total_cliques += num_final_cliques
        total = self.total_cliques

        print(f"Finalized peeling: added {num_final_cliques} from auxiliary solver "
              f"(total cliques = {total})")

        return accumulated_value + total



# class ReduceAndPeel(ReduceAndAct):
#     """
#     Reduce-and-Peel paradigm:
#     - Applies reductions
#     - Finds patterns (C5s or otherwise)
#     - Peels off N[pattern] with a clique cover of it
#     - Repeats until no patterns remain
#     - Finalizes by possibly solving the residual graph
#     """

#     def __init__(self,
#                  reductions,
#                  pat_finder,
#                  pat_choice_heuristic,
#                  pat_neighborhood_evaluator,
#                  auxiliary_solver,
#                  peeled_cover=None):
#         super().__init__(reductions,
#                          pat_finder,
#                          pat_choice_heuristic,
#                          pat_neighborhood_evaluator,
#                          auxiliary_solver)
#         # Store the clique cover constructed during peeling
#         self.peeled_cover = peeled_cover or []

#     def act_on_pattern_neighborhood(self, graph, chosen_neighborhood):
#         """
#         Removes N[pattern], covers it with a clique cover, and
#         adds those cliques to the peeled solution.
#         Returns (next_graph, delta_value), where delta_value can
#         represent the number of cliques added.
#         """

#         # === Step 1: Compute clique cover of N[pattern] ===
#         covered_cliques = self.pat_neighborhood_evaluator(graph, chosen_neighborhood)
#         if not isinstance(covered_cliques, list):
#             raise TypeError("Expected pat_neighborhood_evaluator to return a list of cliques")

#         self.peeled_cover.extend(covered_cliques)

#         # === Step 2: Remove the entire N[pattern] from the graph ===
#         removal_mask = [False] * graph.number_of_nodes()
#         for node in chosen_neighborhood:
#             removal_mask[node] = True
#         next_graph = removed_masked_nodes(graph, removal_mask)

#         delta_value = len(covered_cliques)
#         print(f"Peeling N[pattern] of size {len(chosen_neighborhood)}; "
#               f"added {delta_value} cliques to cover (total = {len(self.peeled_cover)})")

#         return next_graph, delta_value

#     def finalize(self, graph, accumulated_value):
#         """
#         Once no patterns remain, run the auxiliary solver on the remaining graph
#         to complete the cover, and return the final list of cliques.
#         """
#         final_cover = self.auxiliary_solver(graph)
#         if isinstance(final_cover, list):
#             self.peeled_cover.extend(final_cover)
#         else:
#             raise TypeError("Expected auxiliary_solver to return a list of cliques")

#         print(f"Finalized peeling: total cliques = {len(self.peeled_cover)}")
#         return self.peeled_cover
