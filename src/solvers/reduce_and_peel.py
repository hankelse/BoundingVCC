from src.solvers.frameworks.reduce_and_act import ReduceAndAct
from src.solvers.tools.reductions import remove_masked_nodes
from src.structures.graph import Graph



def reduce_and_peel(graph: Graph, **kwargs):
    """Convenience wrapper to run the Reduce-and-Peel algorithm."""
    return ReduceAndPeel(**kwargs).run(graph)

from src.solvers.frameworks.reduce_and_act import ReduceAndAct


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
        # self._clique_cover is tracked by reduce_and_act

    def act_on_pattern_neighborhood(self, graph, chosen_neighborhood):
        """
        Removes N[pattern], covers it with a clique cover, and increments
        the total clique count by the number of cliques returned.
        Returns (next_graph, delta_value), where delta_value is the number
        of cliques added in this step.
        """

        # === Step 1: Compute clique cover of N[pattern] ===
        covering = self.pat_neighborhood_evaluator(graph, chosen_neighborhood)
        self.add_to_cover(covering)

        # Improvement: Check if any other nodes can be added to the covering?

        # === Step 2: Remove N[pattern] from the graph ===
        removal_mask = [False] * graph.number_of_nodes()
        for node in chosen_neighborhood:
            removal_mask[node] = True
        next_graph = remove_masked_nodes(graph, removal_mask)

        self.log(f"Peeling N[pattern] of size {len(chosen_neighborhood)}")

        print(f"started with graph this {graph.nodes()} ending with this: {next_graph.nodes()}")
    

        return next_graph

    def finalize(self, graph):
        """
        Once no patterns remain, run the auxiliary solver on the remaining graph
        and add its clique count to the total.
        Returns the total number of cliques found overall.
        """
        final_cover = self.auxiliary_solver(graph)

        self.add_to_cover(final_cover)
        self.log(f"Finalized peeling: added {len(final_cover)} from auxiliary solver (total cliques = {len(self.get_cover())})")

        return self.get_cover()

