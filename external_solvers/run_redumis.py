import re
import subprocess
from pathlib import Path

def redumis(graph_path, kamis_dir="external_solvers/KaMIS", timeout=None):
    """
    Runs KaMIS/redumis on the given graph file and extracts MIS size.
    """
    graph_path = Path(graph_path)
    executable = Path(kamis_dir) / "redumis"

    cmd = [str(executable), str(graph_path)]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    output = result.stdout.strip()

    # --- Parse independent set size from output ---
    match = re.search(r"Independent set has size\s+(\d+)", output)
    mis_size = int(match.group(1)) if match else None

    return {
        "graph": graph_path.name,
        "returncode": result.returncode,
        "mis_size": mis_size,
        "stdout": output,
        "stderr": result.stderr.strip(),
    }
