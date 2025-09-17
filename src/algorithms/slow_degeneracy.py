from graph import Graph

'''
Given a graph, return a degeneracy ordering and number


This method runs in O(ndlogd + n^2d) which is slower than the O(n + m) from the 1983 paper: "Smallest-Last Ordering and Clustering and Graph Coloring Algorithms"
'''

def get_degeneracy_slow(g : Graph):
    '''
    
    Running time = O(ndlogd + n^2d)
    '''
    graph = g.copy() # O(n + m)
    degen_ordering = []
    degree_ordering = get_degree_ordering(graph) # O (nlogn)
    highest_core_degree = 0

    while len(graph.nodes()) > 0: # O(n)
        # Empty list of affected neighbors
        affected_neighbors = []

        # Find the lowest degree node
        lowest = degree_ordering[0]

        # Update max_degree if node has highest
        if graph.degree(lowest) > highest_core_degree:
            highest_core_degree = graph.degree(lowest)

        # Mark its neighbors
        affected_neighbors = [n for n in graph.neighbors(lowest)] # O(d) --> O(nd)

        # Add to degen ordering and remove from graph and ordering
        degen_ordering.append(lowest)
        graph.remove_node(lowest) # O(n) --> O(n^2)??
        degree_ordering = degree_ordering[1:] #O(n) --> O(n^2)

        # Resort its neighbors
        if len(affected_neighbors) > 0:
            degree_ordering = update_ordering(graph, ordered_nodes=degree_ordering, unsorted=affected_neighbors) # O(dlogd + nd) --> * n
        
    return degen_ordering, highest_core_degree


def get_degree_ordering(graph : Graph):
    """Orders nodes by degree low to high"""
    ordered = sorted(graph.nodes(), key=lambda n: graph.degree(n))
    return ordered

def update_ordering(graph : Graph, ordered_nodes, unsorted):
    """
    Given
        ordered_nodes: the unaffected nodes from the previous ordering (size : n - number of iterations)
        unsorted:  (unaffected neighbor, previous index)
            the unaffected neighbors (size : O(degeneracy number))
            previous index before sorting

    Runs in O(dlogd + nd) time
    """
    # |unsorted| = O(d)

    # Sort the unsorted --> O(dlogd)
    unsorted = sorted(unsorted, key=lambda n: graph.degree(n)) 

    # Build a new ordering by going through ordered nodes until there is a place to insert unsorted one.
    new_ordering = []

    # Track the progress through the unsorted elements
    curr_unsorted_index = 0

    # Track the degree of the current element for speed
    curr_unsorted_degree = graph.degree(unsorted[0])

    # Iterate through ordered --> O(n)
    for n in ordered_nodes: # Skip the 0th, because that was just removed from the graph
        
        # If there are more unsorted nodes to add
        if curr_unsorted_index < len(unsorted):
            n_degree = graph.degree(n)

            # Add all of the unsorted nodes that can go here
            while n_degree >= curr_unsorted_degree: # O(d) <-- not per iteration, in total
                new_ordering.append(unsorted[curr_unsorted_index])

                curr_unsorted_index += 1
                if curr_unsorted_index < len(unsorted):
                    curr_unsorted_degree = graph.degree(unsorted[curr_unsorted_index])
                else:
                    break
        
        # Add the next sorted node, if not one of the changed ones
            # Since nodes lose degree we only have to check for repeats of ones we have already put in
        if n not in unsorted[0:curr_unsorted_index]: # O(d)
            new_ordering.append(n)
    
    return new_ordering




