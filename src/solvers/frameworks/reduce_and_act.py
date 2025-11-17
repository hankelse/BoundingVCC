from abc import ABC, abstractmethod
from src.solvers.tools.reductions import remove_masked_nodes

from src.solvers.tools.evaluate_cover import validate_cover
from src.structures.graph import Graph


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
        
        # Management
        self._node_mapping = None # A mapping of nodes current names to their original ones


        # Tracking
        # self._cliques_removed = []
        self._clique_cover = []
        self._log = ""


    def log(self, message):
        self._log += message + "\n"
    
    def get_log(self):
        return self._log

    def remap_cliques(self, cliques):
        remapped_cliques = []
        for clique in cliques:
            remapped = []
            for node in clique:
                remapped.append(self._node_mapping[node])
            
            remapped_cliques.append(remapped)
        
        return remapped_cliques

    def update_node_mapping(self, graph):
        """
        When a new graph is created, the nodes are relabbeled from 0...[number of nodes] and the graph saves a mapping. 
        As we iteratively solve on smaller graphs, the mappings change so we need to update the internal one so that
        the outputted clique cover is correct.
        """
        new_map = graph.new_to_old_labels   # maps: new → old (prev graph)

        # print(f"Current map: {self._node_mapping} \nNew Info: {new_map}")
        # print(f"Passed a graph of size {graph.number_of_nodes()}")

        if self._node_mapping is None:
            self._node_mapping = {}
            # First graph: map to self
            for node in graph.nodes():
                self._node_mapping[node] = node


            # self._node_mapping = new_map.copy()
            return

        updated = {}

       

        # For every label in the *new* graph:
        for new_label, old_label in new_map.items():
            # old_label refers to labels from the previous graph,
            # which we know how to map back to the original
            updated[new_label] = self._node_mapping[old_label]

        # For labels that were REMOVED in this reduction step,
        # KEEP their old mapping!
        # for missing_old in self._node_mapping:
        #     if missing_old not in new_map.values():
        #         # This original node no longer exists in the graph,
        #         # but must remain unmapped for clique cover purposes
        #         updated[missing_old] = self._node_mapping[missing_old]

        self._node_mapping = updated
        # print(f"Resulting map: {self._node_mapping}")


    def add_to_cover(self, cliques):
        to_be_added = self.remap_cliques(cliques)
        self._clique_cover += to_be_added

    def get_cover(self):
        return self._clique_cover


    @abstractmethod
    def act_on_pattern_neighborhood(self, graph, chosen_pattern):
        """
        Defines how to act on the chosen substructure.
        Should return next_graph.
        """
        pass

    @abstractmethod
    def finalize(self, graph ):
        """
        Called when no more patterns can be found.
        Should return the final result.
        """
        pass

    def run(self, graph : Graph):
        """
        The general iterative reduction and pattern-action loop.
        """
        if graph.number_of_nodes() == 0: return self.finalize(graph)
        self.update_node_mapping(graph)

        # print(self.get_log())

        # 1. Apply reductions

        masked_nodes, cliques = self.reductions(graph)
        reduced = remove_masked_nodes(graph, masked_nodes)

        valid, missing_edges, uncovered_nodes = validate_cover(graph, cliques)
        if missing_edges: 
            print("assumed non-existant edge exists after reductions", missing_edges)
            print(self.get_log())
            input()

        

        #Remap the nodes in cliques to their original values
        self.add_to_cover(cliques)
        

        self.log(f"Reduced Graph from ({graph.number_of_nodes()}, {graph.number_of_edges()}) to ({reduced.number_of_nodes()}, {reduced.number_of_edges()}) finding {len(cliques)} cliques.")

        # 2. Find candidate substructures
        patterns = list(self.pat_finder(reduced))

        self.log(f"Found {len(patterns)} patterns")

        if not patterns:
            # No patterns left → finalize
            self.log(f"Running finalization on graph ({reduced.number_of_nodes()}, {reduced.number_of_edges()})")
            return self.finalize(reduced)

        # 3. Choose one, gets its neighborhood
        chosen_neighborhood = self.pat_choice_heuristic(reduced, patterns)

        self.log(f"Chose pattern neighborhood of size {len(chosen_neighborhood)}")

        # 4. Perform subclass-defined action
        self.update_node_mapping(reduced)
        next_graph = self.act_on_pattern_neighborhood(reduced, chosen_neighborhood)

        self.log(f"After action, recurring on graph ({next_graph.number_of_nodes()}, {next_graph.number_of_edges()})")


        # 5. Recurse
        return self.run(next_graph)
