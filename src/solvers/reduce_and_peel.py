from src.solvers.frameworks.reduce_and_act import ReduceAndAct
from src.solvers.tools.reductions import remove_masked_nodes
from src.structures.graph import Graph
from src.solvers.tools.external_solvers import unwind_cover
from src.solvers.tools.evaluate_cover import validate_cover
from src.data_io.load_data import load_metis_graph



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

        self._peeled_stack = []
        self._labell_maps_stack = []
        self._num_cliques_peeled = 0
        self._cover_size = 0

        self._final_cover = [] # A covering provided by the auxillary solver

    def _push_peeled(self, cliques):
        '''
        Pushes a set of cliques or a single clique, (all of the cliques found from act_on_pattern_neighborhood)
        Onto a stack to later rebuild
        '''
        if not isinstance(cliques[0], list):
            cliques = [cliques]
        
        self._num_cliques_peeled += len(cliques)
        self._peeled_stack.append(cliques)

    def _pop_peeled(self):
        '''Pops a list of cliques from the _peeled_stack'''
        return self._peeled_stack.pop()


    def act_on_pattern_neighborhood(self, graph : Graph, chosen_neighborhood):
        """
        Removes N[pattern], covers it with a clique cover, and increments
        the total clique count by the number of cliques returned.
        Returns (next_graph, delta_value), where delta_value is the number
        of cliques added in this step.
        """
        self.log(f"Running {self.pat_neighborhood_evaluator.__name__}")


        # === Step 1: Compute clique cover of N[pattern] ===
        covering = self.pat_neighborhood_evaluator(graph, chosen_neighborhood)
        remapped_covering = covering
        self._push_peeled(remapped_covering) # Updates self._num_cliques_peeled

        self.log(f"Pushed cover {covering} --> {remapped_covering} onto the stack")

        # Improvement: Check if any other nodes can be added to the covering?

        # === Step 2: Remove N[pattern] from the graph ===
        removal_mask = [False] * graph.number_of_nodes()
        for node in chosen_neighborhood: removal_mask[node] = True
        next_graph = remove_masked_nodes(graph, removal_mask)

        self.log(f"Peeling N[pattern] of size {len(chosen_neighborhood)}:  {chosen_neighborhood}")

        self._labell_maps_stack.append(next_graph.new_to_old_labels)
        self.log(f"Putting label map onto stack {next_graph.new_to_old_labels}")

        return next_graph

    def finalize(self, graph):
        """
        Once no patterns remain, run the auxiliary solver on the remaining graph
        and add its clique count to the total.
        Returns the total number of cliques found overall.
        """
        if graph.number_of_nodes() != 0:
            self._final_cover = self.auxiliary_solver(graph)
            num_final_cover_cliques = len(self._final_cover)
        else:
            self._final_cover = []
            num_final_cover_cliques = 0

        # self.add_to_cover(self._final_cover)
        self.log(f"Finalized peeling: added {len(self._final_cover)} from auxiliary solver (total cliques = {len(self.get_cover())})")

        total_num_cliques = num_final_cover_cliques + self._num_cliques_from_reductions + self._num_cliques_peeled
        return total_num_cliques
    
    def build_cover(self):
        '''
        After a completed run of the algorithm, this method can be 
        used to construct a clique cover corresponding to the upper 
        bound calculated.
        '''

        self.log("\nSTARTING BUILD COVER\n" + f"\nPEELED_STACK: {self._peeled_stack}" + "\nGRAPH_STACK: {self._graph_stack}\n")

        current_cover = self._final_cover

         # If we finished after a peel, add it to the current cover to normalize
        if len(self._peeled_stack) == len(self._graph_stack):
            current_cover += self._pop_peeled()
            self._labell_maps_stack = self._labell_maps_stack[:-1]
            self.log("Algorithm finished on a peel so getting first cover from peel stack not from aux solver result: " + str(current_cover))

        # Sanity check that stacks are appropriate sizes
        assert len(self._graph_stack) == len(self._peeled_stack) + 1, f"Unexpected sizes graph_stack={len(self._graph_stack)}, peeled={len(self._peeled_stack)}"

        # Now we have a covering of the Graph provided after the final round of reductions
        while len(self._peeled_stack) != 0:
            destination_graph = self._pop_graph_path()
            print(f"Unwinding to a cover of {destination_graph}")

            # from src.solvers.tools.reductions import apply_reductions_external
            # G = load_metis_graph(destination_graph)
            # reduced, clique_offset, removed_cliques = apply_reductions_external(G, "debug_graph.txt")
            # # print("Going to pass G to unwing, G.edges:", G.edges())
            # print("artifically reduced G, giving", reduced.edges())
            

            


            #1 Unwind the most recent reductions
            current_cover = unwind_cover(current_cover, destination_graph)

            # Assert that current cover is a cover of G

            # print(f"Unwound cover = {current_cover}")

            # Assert that current cover is a cover of 
            # result, missing, uncovered = validate_cover(G, current_cover)
            # if result == False:
            #     print(missing, uncovered)
            #     input()
            # else:
            #     print("COVER CHECKED")


            # We need to remapped the nodes before popping the peeled...
            new_to_old_map = self._labell_maps_stack.pop()
            # print(f"Label map: ", new_to_old_map)

            remapped_cover = self.remap_cliques(current_cover, new_to_old_map)
            # print(f"Remapped complete cover \n\t{current_cover} to \n\t{remapped_cover}")
            
            #2 Undo the most recent peel
            last_peel = self._pop_peeled()
            # print(f"Popped the last peel", last_peel)
            current_cover =  last_peel + remapped_cover
            # print(f"Finally: \n\t{current_cover}")

            # # Validate that it is a covering to the reduction of the next graph on the stack
            # next_G = load_metis_graph(self._graph_stack[-1])
            # reduced, clique_offset, removed_cliques = apply_reductions_external(next_G, "debug_graph1.txt")
            # # print(f"That should be a cover for: \n\t{reduced.edges()}")
            # result, missing, uncovered = validate_cover(reduced, current_cover)
            # if result == False:
            #     print("Did not cover properly.")
            #     print(missing, uncovered)
            #     input()
            # else:
            #     print("COVER CHECKED")


        
        # If the peeled stack is empty, current cover is a covering of the original graph's reduction
        assert len(self._graph_stack) == 1, "The graph stack is empty prematurely!"


        current_cover = unwind_cover(current_cover, self._pop_graph_path())

        return current_cover
        


