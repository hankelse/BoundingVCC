from src.structures.graph import Graph
from src.structures.bucket_queue import BucketQueue
from collections import deque

'''
Given a graph, return a degeneracy ordering and number 
from the 1983 paper: "Smallest-Last Ordering and Clustering and Graph Coloring Algorithms"
'''

def get_degeneracy(graph : Graph):
    # Input: graph G (networkx.Graph)
    # Output: degeneracy_ordering (list of nodes), degeneracy_number (int)

    """
    Compute degeneracy ordering in O(n + m) using a bucket queue.
    """

    # Initialize bucket queue: one bucket for each possible degree (0 ... max_deg)
    b_queue = BucketQueue(graph.max_degree())

    # Push each node into bucket[degree[v]]
    for n in graph.nodes():
        b_queue.push(key=graph.degree(n), item=n)

    # Set up a degree map for as the degrees change:
    curr_degree = [-1] * graph.number_of_nodes()
    for node in graph.nodes(): 
        # print(node, len(curr_degree))
        curr_degree[node] = graph.degree(node)
    
    # Initialize result structures
    degeneracy_ordering, degen_number = [], 0

    # Initialize a lookup table to O(1) check if we have already added a node to the queue
    already_added = [False for node in graph.nodes()]
    
    # While queue not empty
    while not b_queue.is_empty():
    #   1. Pop the next node from the lowest non-empty bucket (O(1) average)                        Since we don't delete nodes, we need to check if they are already added later.
        node = b_queue.pop_min()
        while node != None and already_added[node]: 
            node = b_queue.pop_min()
        if node == None: break

        already_added[node] = True

    #   2. Record node in ordering
        degeneracy_ordering.append(node)

    #   3. Update degen_number
        degen_number = max(curr_degree[node], degen_number)
        # print(f"Added node {node} which has {curr_degree[node]} later neighbors")

    #   4. For each neighbor u of v that is still in the graph:
        for neighbor in graph.neighbors(node):
            if already_added[neighbor]: continue # Skip already added neighbors

            # Adjust degrees
            curr_degree[neighbor] -= 1
            b_queue.push(key=curr_degree[neighbor], item=neighbor)
    
    return degeneracy_ordering, degen_number



def compute_later_neighbors(graph: Graph, degeneracy_ordering):
    """
    Given a graph and its degeneracy ordering, 
    Returns a map, later_neighbors where
        key (node) : value (list of later neighbors)

    Runs in O(n + m) time

    Assumptions: 
                Node_ids go from 0..|V|-1
                No two nodes can have the same index in degen ordering
    """

    # 1) Create a node_id to degen_index lookup "map": degen_index 
    # O(n)
    degen_indices = [-1] * graph.number_of_nodes()
    for degen_index, node in enumerate(degeneracy_ordering):
        degen_indices[node] = degen_index

    # 2) Create the later_neighbors map
    # O(n)
    later_neighbors = {node : [] for node in graph.nodes()} 

    # 3) Fill the later_neighbors map
    # O(m)
    for u, v in graph.edges():
        u_d_index = degen_indices[u]
        v_d_index = degen_indices[v]

        if u_d_index < v_d_index:
            later_neighbors[u].append(v)
        else:
            later_neighbors[v].append(u)
    
    return later_neighbors




