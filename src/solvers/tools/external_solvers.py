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


def find_clique_cover(graph):
    if graph.number_of_nodes() == 0: return []

    graph.write(output_path="temp.txt", file_type="metis")

    result = reduvcc(graph_path="temp.txt")
    # print(result)
    cover = read_clique_cover(path="redu_cover_cliques.txt")
    # print(cover)

    return cover




def read_clique_cover(path: str, one_indexed: bool = True):
    """
    Reads a clique-cover file where each line contains space-separated vertex IDs.
    Returns a list of cliques, where each clique is a list[int].

    Args:
        path (str): Path to file (e.g., "removed_cliques.txt").
        one_indexed (bool): If True, convert vertex IDs from 1-indexed to 0-indexed.

    Returns:
        list[list[int]]: List of cliques, each a list of ints.

    *** ALL LABELS ARE OFFSET BY 1 *** 
    """
    cliques = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # parse numbers
            parts = line.split()
            try:
                clique = [int(x) for x in parts]
            except ValueError:
                # skip lines that aren't properly formatted
                continue

            # convert to 0-indexed if needed
            if one_indexed:
                clique = [v - 1 for v in clique]

            cliques.append(clique)

    return cliques
