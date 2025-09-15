import networkx as nx
import matplotlib.pyplot as plt
# My Graph Class that creates and wraps around a nxGraph
class Graph:
    def __init__(self, edge_list):
        # Remap edges
        new_edges, mapping = remap_nodes(edge_list)
        # Store mappings
        self.old_to_new_labels = mapping
        self.new_to_old_labels = {v: k for k, v in mapping.items()}

        # Create Graph
        self._graph = nx.Graph()
        self._graph.add_edges_from(new_edges)

    def nodes(self):
        """Return node list."""
        return list(self._graph.nodes())

    def edges(self):
        """Return edge list."""
        return list(self._graph.edges())
    
    import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, edge_list, name=None):
        self.name = name

        # Remap edges
        new_edges, mapping = remap_nodes(edge_list)
        # Store mappings
        self.old_to_new_labels = mapping
        self.new_to_old_labels = {v: k for k, v in mapping.items()}

        # Create Graph
        self._graph = nx.Graph()
        self._graph.add_edges_from(new_edges)

    # === Get data on the Graph === #
    def report_sizes(self):
        """
        Prints:
        - number of nodes
        - number of edges
        - average degree
        - maximum degree
        """
        num_nodes = self._graph.number_of_nodes()
        num_edges = self._graph.number_of_edges()

        if num_nodes > 0:
            avg_degree = sum(dict(self._graph.degree()).values()) / num_nodes
            max_degree = max(dict(self._graph.degree()).values())
        else:
            avg_degree = 0
            max_degree = 0

        print(f"Graph: {self.name}")
        print(f"\tNodes: {num_nodes}")
        print(f"\tEdges: {num_edges}")
        print(f"\tAverage degree: {avg_degree:.2f}")
        print(f"\tMax degree: {max_degree}")

    # === Editing the Graph ===
    def add_node(self, u):
        """Add a node to the graph."""
        self._graph.add_node(u)

    def add_edge(self, u, v):
        """Add an edge to the graph (adds nodes if needed)."""
        self._graph.add_edge(u, v)

    def remove_node(self, u):
        """Remove a node and its incident edges."""
        self._graph.remove_node(u)

    def remove_edge(self, u, v):
        """Remove an edge between two nodes (if it exists)."""
        self._graph.remove_edge(u, v)

    def copy(self):
        """
        Returns a deep copy of the graph.
        Mutations on the copy do not affect the original.
        """
        new_graph = Graph([], name=self.name)
        new_graph._graph = self._graph.copy(as_view=False)
        new_graph.old_to_new_labels = dict(self.old_to_new_labels)
        new_graph.new_to_old_labels = dict(self.new_to_old_labels)
        return new_graph
    
    # === Wrappers around common networkx methods ===
    def nodes(self):
        """Return node list."""
        return list(self._graph.nodes())

    def edges(self):
        """Return edge list."""
        return list(self._graph.edges())

    def neighbors(self, node):
        """Return neighbors of a node."""
        return list(self._graph.neighbors(node))
    
    def degree(self, node):
        """Return degree of a node."""
        if node not in self._graph:
            raise ValueError(f"Node {node} is not in the graph.")
        return self._graph.degree[node]


    def has_edge(self, u, v):
        """Check if an edge exists between u and v."""
        return self._graph.has_edge(u, v)

    def subgraph(self, nodes):
        """Return a new Graph object induced by 'nodes'."""
        sub_edges = self._graph.subgraph(nodes).edges()
        return Graph([(self.new_to_old_labels[u], self.new_to_old_labels[v]) for u, v in sub_edges])

    def number_of_edges(self):
        """Return the number of edges."""
        return self._graph.number_of_edges()

    def number_of_nodes(self):
        """Return the number of nodes."""
        return self._graph.number_of_nodes()
    
    # == Remapping node ids == 

    def original_label(self, node):
        """Get the original label for a remapped node."""
        if node not in self.new_to_old_labels: raise ValueError(f"Remapped node {node} does not exist in this graph.")
        return self.new_to_old_labels[node]

    def remapped_label(self, original):
        """Get the remapped label for an original node."""
        if original not in self.old_to_new_labels: raise ValueError(f"Original node {original} does not exist in this graph.")
        return self.old_to_new_labels[original]
    
    def show(self):
        """Draw the graph with matplotlib."""
        nx.draw(self._graph, with_labels=True, node_color="lightblue", edge_color="gray")
        plt.show()

    def nx_graph(self):
        # Ideally won't be used, (until I get lazy)
        """Expose the underlying networkx graph (remapped)."""
        return self._graph
    


# Function for remapping node labels from an edge list:
def remap_nodes(edge_list):
    """
    Remap node labels in an edge list so they go from 0 to num_nodes-1.
    
    Returns:
        new_edges : list of (u, v)
        mapping :  old labels -> new labels.
    """
    # Collect all unique nodes
    nodes = sorted(set(u for edge in edge_list for u in edge))
    
    # Build mapping old -> new
    mapping = {old: new for new, old in enumerate(nodes)}
    
    # Apply mapping to edges
    new_edges = [(mapping[u], mapping[v]) for (u, v) in edge_list]
    
    return new_edges, mapping
