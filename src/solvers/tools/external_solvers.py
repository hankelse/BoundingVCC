from src.structures.graph import Graph
from external_solvers.run_redumis import redumis
from external_solvers.run_reduvcc import reduvcc

def find_indepedent_set_size(graph : Graph):
    if graph.number_of_nodes() == 0: return 0

    graph.write(output_path="temp.txt", file_type="metis")
    result = redumis(graph_path="temp.txt")

    print(f"Independent Set Size: {result['mis_size']}")

    return result['mis_size']

def find_clique_cover_size(graph):
    """
    Runs ReduVCC on the given graph and returns the clique cover size.
    The graph is first written to a temporary METIS file.
    """
    if graph.number_of_nodes() == 0: return 0

    graph.write(output_path="temp.txt", file_type="metis")

    result = reduvcc(graph_path="temp.txt")
    cover_size = None
    if "details" in result and "clique_cover_size" in result["details"]:
        cover_size = result["details"]["clique_cover_size"]

    print(f"Clique Cover Size: {cover_size}")

    return cover_size
