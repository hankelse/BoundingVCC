from src.structures.graph import Graph
from external_solvers.run_redumis import redumis
from external_solvers.run_reduvcc import reduvcc
from pathlib import Path
from tempfile import TemporaryDirectory
import os


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

    # Sanity Checks 
    import itertools
    for clique in cover:
        edges = list(itertools.combinations(clique, 2))
        for u, v in edges:
            assert graph.has_edge(u, v), "find clique cover found invalid clique"
            assert u in graph.nodes(), f"find clique cover covered {u} which is not in graph"
    return cover


from external_solvers.run_redu_unwind import redu_unwind


def unwind_cover(cover, destination_graph_path, debug_mode=False):
    """
    Unwinds Redu reductions by providing a kernel clique cover C'
    and letting ReduVCC reconstruct the full cover of the original graph.

    Parameters
    ----------
    graph : Graph
        Must support graph.write(output_path, file_type="metis")

    cliques : list[list[int]]
        Clique cover C' of the reduced graph G' (0-based)

    reduvcc_dir : str
        Directory containing the ReduVCC 'vcc' executable.

    Returns
    -------
    list[list[int]]
        The fully unwound clique cover of the original graph G,
        with all clique lists 0-indexed.
    """

    # ------------------------------------------------------------
    # 1. Write the input graph G → graph.metis
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # 2. Write kernel clique cover C' → kernel_cover.txt
    #    (ReduUnwind expects 1-indexed node IDs)
    # ------------------------------------------------------------
    kernel_cover_path = Path("kernel_cover.txt")
    # input(f"1: Before writing {cover}")
    write_clique_cover(kernel_cover_path, cover, offset=0)

    
    # ------------------------------------------------------------
    # 3. Run ReduUnwind through the Python wrapper
    # ------------------------------------------------------------
    # input("2")
    result = redu_unwind(
        graph_path=destination_graph_path,
        kernel_cover_path=kernel_cover_path
    )
    # input("3")

    # Validate that ReduUnwind ran successfully
    if result["returncode"] != 0:
        raise RuntimeError(
            f"ReduUnwind failed:\n"
            f"STDOUT:\n{result['stdout']}\n"
            f"STDERR:\n{result['stderr']}"
        )
    
    if debug_mode:
        print(f"STDOUT:\n{result['stdout']}\n"
            f"STDERR:\n{result['stderr']}")

    # ------------------------------------------------------------
    # 4. Read full cover from unwound_cover.txt using read_clique_cover
    # ------------------------------------------------------------
    unwound_path = Path("unwound_cover.txt")
    # if not unwound_path.exists():
    #     raise FileNotFoundError(
    #         f"ReduUnwind did not produce unwound_cover.txt"
    #     )

    # 0-index conversion happens automatically if zero_index=True
    full_cover = read_clique_cover(unwound_path, zero_index=False)

    return full_cover




from pathlib import Path

def write_clique_cover(path, cover, offset=1):
    with path.open("w") as f:
        for clq in cover:
            f.write(" ".join(str(v+offset) for v in clq) + "\n")
    # file is CLOSED here -> everything flushed safely


def read_clique_cover(path: str | Path, zero_index: bool = True):
    """
    Reads a ReduVCC 'removed_cliques.txt' style file.

    - Ignores comment lines starting with '#'
    - One clique per non-empty line
    - Nodes are 1-indexed in the file; if zero_index=True, subtract 1.

    Returns:
        list[list[int]]: list of cliques, each a list of node indices.
    """
    path = Path(path)
    cliques: list[list[int]] = []

    if not path.exists():
        # No clique information – treat as no cliques removed.
        return cliques

    with path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            clique_nodes: list[int] = []
            for token in line.split():
                try:
                    node_id = int(token)
                except ValueError:
                    # Skip anything non-numeric just in case
                    continue

                if zero_index:
                    node_id -= 1  # convert 1-based METIS → 0-based internal

                clique_nodes.append(node_id)

            if clique_nodes:
                cliques.append(clique_nodes)

    return cliques

