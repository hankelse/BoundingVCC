from abc import ABC, abstractmethod
from src.algorithms.reductions import removed_masked_nodes


class ReduceAndAct(ABC):
    """
    Abstract base class for algorithms that iteratively:
      1. Apply reductions
      2. Find substructures (patterns)
      3. Choose one based on a heuristic
      4. Perform an 'action' (defined by subclass)
      5. Recur or terminate with a final solver
    """

    def __init__(self,
                 reductions,
                 pat_finder,
                 pat_choice_heuristic,
                 pat_neighborhood_evaluator,
                 auxiliary_solver):
        self.reductions = reductions
        self.pat_finder = pat_finder
        self.pat_choice_heuristic = pat_choice_heuristic
        self.pat_neighborhood_evaluator = pat_neighborhood_evaluator
        self.auxiliary_solver = auxiliary_solver

    # === Hook methods ===

    @abstractmethod
    def act_on_pattern_neighborhood(self, graph, chosen_pattern):
        """
        Defines how to act on the chosen substructure.
        Should return (next_graph, value_delta).
        """
        pass

    @abstractmethod
    def finalize(self, graph, accumulated_value):
        """
        Called when no more patterns can be found.
        Should return the final result.
        """
        pass

    # === Template method ===

    def run(self, graph, accumulated_value=0):
        """
        The general iterative reduction and pattern-action loop.
        """
        # 1. Apply reductions
        masked_nodes, cliques = self.reductions(graph)
        reduced = removed_masked_nodes(graph, masked_nodes)
        accumulated_value += len(cliques)

        # 2. Find candidate substructures
        patterns = list(self.pat_finder(reduced))

        if not patterns:
            # No patterns left → finalize
            return self.finalize(reduced, accumulated_value)

        # 3. Choose one, gets its neighborhood
        chosen_neighborhood = self.pat_choice_heuristic(reduced, patterns)

        # 4. Perform subclass-defined action
        next_graph, delta_value = self.act_on_pattern_neighborhood(reduced, chosen_neighborhood)

        # 5. Recurse
        return self.run(next_graph, accumulated_value + delta_value)
