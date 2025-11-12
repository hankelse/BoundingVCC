import re
import subprocess
from pathlib import Path

def reduvcc(graph_path, reduvcc_dir="external_solvers/ReduVCC/optimized", timeout=None):
    """
    Runs ReduVCC on the given graph file and extracts key statistics.
    Example output includes lines like:
        data/snap_datasets_metis/p2p-Gnutella04.metis, 10879, 79988, 0, 0.011333, 0
        ...
        BEGIN_OUTPUT_FOR_TABLES
        run_type=ReduVCC
        input_graph_vertices=10879
        input_graph_edges=39994
        reduced_graph_vertices=0
        reduced_graph_edges=0
        total_time_to_best=0.00039196
        time_to_best_without_unwind=-1.90735e-06
        clique_cover_size=6531
        verified_cover=passed
        optimal=unknown
    """
    graph_path = Path(graph_path)
    executable = Path(reduvcc_dir) / "vcc"

    cmd = [
        str(executable),
        "--preconfiguration=fsocial",
        "--k=2",
        "--run_type=ReduVCC",
        str(graph_path)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    output = result.stdout.strip()

    # --- Parse the summary line (first CSV-like line) ---
    summary_match = re.search(
        r"([\w/.-]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+),\s*(\d+)",
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

    # --- Parse detailed section (BEGIN_OUTPUT_FOR_TABLES) ---
    details = {}
    if "BEGIN_OUTPUT_FOR_TABLES" in output:
        for line in output.splitlines():
            if "=" in line:
                key, value = line.strip().split("=", 1)
                # Convert numeric values when possible
                if re.match(r"^-?\d+\.\d+$", value):
                    value = float(value)
                elif re.match(r"^-?\d+$", value):
                    value = int(value)
                details[key.strip()] = value

    return {
        "graph": graph_path.name,
        "returncode": result.returncode,
        "stdout": output,
        "stderr": result.stderr.strip(),
        "summary": summary,
        "details": details,
    }
