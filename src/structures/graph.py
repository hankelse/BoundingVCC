import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, edge_list, name=None, nodes=None):
        self.name = name

        if nodes == None: nodes = []


        # Remap edges
        new_nodes, new_edges, mapping = remap_nodes_and_edges(node_list=nodes, edge_list=edge_list)
        
        # Store mappings
        self.old_to_new_labels = mapping
        self.new_to_old_labels = {v: k for k, v in mapping.items()}

        # Remove Self loops
        new_edges = remove_self_loops(new_edges)

        # Create Graph
        self._graph = nx.Graph()
        self._graph.add_edges_from(new_edges)

        self._graph.add_nodes_from(new_nodes) # Adds all nodes mentioned in an edge and all in passed in nodes list

        # Add manual edge lookup
        self.edge_set = set(self._graph.edges())

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
        # return self._graph.has_edge(u, v)
        return (u, v) in self.edge_set or (v, u) in self.edge_set

    def subgraph(self, nodes, carry_remapping=True):
        """Return a new Graph object induced by 'nodes'."""
        sub_edges = self._graph.subgraph(nodes).edges()
        sub_nodes = nodes
        if carry_remapping:
            og_sub_edges = [(self.new_to_old_labels[u], self.new_to_old_labels[v]) for u, v in sub_edges]
            og_nodes = [self.new_to_old_labels[n] for n in nodes]
            sub_edges = og_sub_edges
            sub_nodes = og_nodes

        return Graph(edge_list=sub_edges, nodes=sub_nodes, name=str(self.name + "~"))
    

    def number_of_edges(self):
        """Return the number of edges."""
        return self._graph.number_of_edges()

    def number_of_nodes(self):
        """Return the number of nodes."""
        return self._graph.number_of_nodes()

    def max_degree(self):
        """Return the max degree in the graph."""
        degrees = dict(self._graph.degree())
        return max(degrees.values()) if degrees else 0
    
    # == Removal == 

    def copy_without(self, not_included, carry_mapping=True):
        if carry_mapping: 
            #get originally labelled versions
            og_not_included = [self.new_to_old_labels[n] for n in not_included]
            og_nodes = [self.new_to_old_labels[n] for n in self.nodes()]
            og_edges = [(self.new_to_old_labels[u], self.new_to_old_labels[v]) for u, v in self.edges()]


            # Copy over nodes
            og_not_included_set = set(og_not_included)
            new_nodes = []
            for n in og_nodes:
                if not n in og_not_included_set:
                    new_nodes.append(n)
            
            # Copy over edges
            new_edges = []
            for u, v in og_edges:
                if u in og_not_included_set: continue
                if v in og_not_included_set: continue
                new_edges.append((u, v))
        else:
            new_edges = []
            new_nodes = []
            for u, v in self.edges():
                if u in not_included: continue
                if v in not_included: continue
                new_edges.append((u, v))
            for u in self.nodes():
                if u in not_included: continue
                new_nodes.append(u)
            
        # Create graph
        result = Graph(new_edges, name=str(self.name+"*"), nodes=new_nodes)
        return result
    
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
    

    def write(self, output_path, file_type="metis"):
        """
        Write the graph to disk in the specified format.
        """
        import os

        file_type = file_type.lower()
        if file_type not in {"metis", "snap"}:
            raise ValueError(f"Unsupported file type '{file_type}'. Use 'metis' or 'snap'.")

        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        n = self._graph.number_of_nodes()
        m = self._graph.number_of_edges()
        nodes_sorted = sorted(self._graph.nodes())

        assert nodes_sorted[0] == 0, "graph was corrupted when writing to metis"

        if file_type == "metis":
            with open(output_path, "w") as f:
                # OFFSET by 1 for metis
                f.write(f"{n} {m}\n")
                offset = 1
                for node in nodes_sorted:
                    neighbors = sorted(self._graph.neighbors(node))
                    neighbors = [str(v + offset) for v in neighbors]
                    f.write(" ".join(neighbors) + "\n")

        elif file_type == "snap":
            with open(output_path, "w") as f:
                f.write("# SNAP-format edge list\n")
                for u, v in self._graph.edges():
                    f.write(f"{u} {v}\n")

        # print(f"Wrote {file_type.upper()} file: {output_path}")



    


# Function for remapping node labels from an edge list:
def remap_nodes_and_edges(node_list, edge_list):
    """
    Remap node labels from an node list so they go from 0 to num_nodes-1.
    
    Returns:
        new_edges : list of (u, v)
        mapping :  old labels -> new labels.
    """
    # Collect all unique nodes, combine with any implied by edges
    nodes = set()
    for u, v in edge_list:
        nodes.add(u)
        nodes.add(v)
    for n in node_list:
        nodes.add(n)
    
    # Build mapping old -> new
    mapping = {old: new for new, old in enumerate(nodes)}

    # Apply mapping to nodes
    new_nodes = [mapping[n] for n in nodes]
    
    # Apply mapping to edges
    new_edges = [(mapping[u], mapping[v]) for (u, v) in edge_list]
    
    return new_nodes, new_edges, mapping



def remove_self_loops(edge_list):
    return [(u, v) for (u, v) in edge_list if u != v]
