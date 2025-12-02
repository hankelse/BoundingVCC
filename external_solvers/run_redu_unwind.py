import re
import subprocess
from pathlib import Path

def redu_unwind(
    graph_path,
    kernel_cover_path,
    reduvcc_dir="external_solvers/ReduVCC/optimized",
    timeout=None,
):
    """
    Runs ReduVCC in ReduUnwind mode.

    Parameters
    ----------
    graph_path : str or Path
        Path to the ORIGINAL METIS graph G.
    kernel_cover_path : str or Path
        Path to the clique cover of the REDUCED graph G' (kernel).
        This file must contain one clique per line, 0-based or 1-based.
    reduvcc_dir : str
        Directory where the compiled ReduVCC binary lives.
    timeout : float or None
        Optional subprocess timeout.

    Returns
    -------
    dict containing:
        - returncode
        - stdout
        - stderr
        - summary (optional parsed CSV header)
        - details (BEGIN_OUTPUT_FOR_TABLES section)
    """

    graph_path = Path(graph_path)
    kernel_cover_path = Path(kernel_cover_path)
    executable = Path(reduvcc_dir) / "vcc"

    # NOTE: ReduUnwind needs TWO path arguments, but we can only pass one so we combinde them and split
    cmd = [
        str(executable),
        "--preconfiguration=fsocial",
        "--k=2",
        "--run_type=ReduUnwind",
        str(graph_path) + "@@@" + str(kernel_cover_path),
    ]
    '''
    ./external_solvers/ReduVCC/optimized/vcc --preconfiguration=fsocial --k=2 --run_type=ReduUnwind reduce_and_actG0.metis@@@kernel_cover.txt
    '''

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    # ----------------------------------------------------------
    # Try to parse CSV-style summary line (if present)
    # ----------------------------------------------------------
    summary_match = re.search(
        r"([\w/.\-]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+),\s*(\d+)",
        stdout
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

    # ----------------------------------------------------------
    # Parse BEGIN_OUTPUT_FOR_TABLES
    # ----------------------------------------------------------
    details = {}
    if "BEGIN_OUTPUT_FOR_TABLES" in stdout:
        for line in stdout.splitlines():
            if "=" in line:
                key, value = line.strip().split("=", 1)

                # Convert numbers when possible
                if re.match(r"^-?\d+\.\d+$", value):
                    value = float(value)
                elif re.match(r"^-?\d+$", value):
                    value = int(value)

                details[key.strip()] = value

    return {
        "graph": graph_path.name,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "summary": summary,
        "details": details,
    }