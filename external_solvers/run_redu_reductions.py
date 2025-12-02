import re
import subprocess
from pathlib import Path


def reduvcc_reductions(graph_path, reduvcc_dir="external_solvers/ReduVCC/optimized", timeout=None):
    """
    Runs ReduVCC in 'Redu' mode to apply data reductions on a graph.

    Example output (after Hank's modification):

        data/snap_datasets_metis/p2p-Gnutella04.metis, 10879, 79988, 0, 0.0106261, 0
        Removed cliques (cover size offset): 6531
        Hank Addition: Wrote reduced graph to reduced_graph.metis with 0 nodes.

    Returns a dictionary with parsed information including:
        - summary: parsed from the first CSV-like line
        - removed_cliques: integer from "Removed cliques" line
        - reduced_graph_nodes: integer from "Wrote reduced graph..." line
    """
    graph_path = Path(graph_path)
    executable = Path(reduvcc_dir) / "vcc"

    cmd = [
        str(executable),
        "--preconfiguration=fsocial",
        "--k=2",
        "--run_type=Redu",
        str(graph_path)
    ]

    # print("before deep")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    # print("after deep")

    output = result.stdout.strip()

    # --- Parse the summary line (CSV-like) ---
    summary_match = re.search(
        r"([\w/.\-]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+),\s*(\d+)",
        output
    )
    summary = None
    if summary_match:
        summary = {
            "graph_path": summary_match.group(1),
            "vertices": int(summary_match.group(2)),
            "edges": int(summary_match.group(3)),
            "reductions": int(summary_match.group(4)),
            "runtime": float(summary_match.group(5)),
            "initial_result": int(summary_match.group(6)),
        }

    # --- Parse "Calculated offset : X" ---
    removed_match = re.search(r"Calculated offset\s*:\s*(\d+)", output)
    offset = int(removed_match.group(1)) if removed_match else None

    # --- Parse "Wrote reduced graph to reduced_graph.metis with X nodes." ---
    reduced_match = re.search(
        r"Wrote reduced graph to reduced_graph\.metis with\s+(\d+)\s+nodes", output
    )
    reduced_graph_nodes = int(reduced_match.group(1)) if reduced_match else None


    return {
        "graph": graph_path.name,
        "returncode": result.returncode,
        "stdout": output,
        "stderr": result.stderr.strip(),
        "summary": summary,
        "cliques_offset": offset,
        "reduced_graph_nodes": reduced_graph_nodes,
    }


# Example usage:
if __name__ == "__main__":
    result = reduvcc_reductions("data/snap_datasets_metis/p2p-Gnutella04.metis")
    print(result)
