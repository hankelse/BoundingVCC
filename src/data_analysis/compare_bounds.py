import csv
import time
from src.data_analysis.optimal_cover_sizes import optimal_cover_sizes
from src.data_io.process_data import get_graphs
from src.solvers.independence_bound import independence_bound
from src.solvers.reduce_and_bound import reduce_and_bound
import traceback, signal


def evaluate_bounds_on_datasets(
    datasets,
    rab_algorithm=reduce_and_bound,
    ib_algorithm=independence_bound,
    output_path="bounds_results.csv",
    timeout=60
):
    """
    Evaluate two lower-bound algorithms across multiple graph datasets
    and save results to a tab-separated CSV, including known optimal
    clique cover sizes when available.
    """
    timed_out = []  # store datasets that timed out

    # --- Load graph dataset map ---
    _, _, _, _, graph_load_fn_map = get_graphs()

    # --- Prepare CSV output ---
    description = algorithm_description(rab_algorithm)
    print(f"description = {description}")

    header = [
        "dataset_category",
        "dataset_name",
        "num_nodes",
        "num_edges", 
        "calculation algorithm",
        "reference algorithm",
        "calculated_bound",
        "reference_bound",
        "optimal_cover_size",
        "difference",
        "calculated_bound_time",
        "reference_bound_time"
    ]

    def algorithm_name(fn):
        """Return a readable algorithm name (for partials, etc.)"""
        return getattr(fn, "__name__", repr(fn))

    # --- Write CSV output ---
    with open(output_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t")

        for desc in description:
            writer.writerow([f"# {desc}"])
        writer.writerow(header)

        for dataset_category, dataset_name in datasets:
            print(f"\n=== Processing {dataset_category}/{dataset_name} ===")

            # --- Load and describe graph ---
            graph = graph_load_fn_map[(dataset_category, dataset_name)]()
            graph.report_sizes()

            # --- Get dataset key and lookup optimal cover size ---
            dataset_key = dataset_name.replace(".txt", "")
            optimal_value = optimal_cover_sizes.get(dataset_key, -1) # default -1

            # --- Helper to time algorithms ---
            def time_algorithm(algorithm, *args, **kwargs):
                start = time.time()
                result = run_algorithm_with_timeout(algorithm, *args, **kwargs)
                duration = round(time.time() - start, 3)
                return result, duration

            # --- Run algorithms ---
            rab_result, rab_time = time_algorithm(
                lambda g: rab_algorithm(g), graph, timeout=timeout
            )
            if rab_result is None:
                timed_out.append((dataset_category, dataset_name))

            ib_result, ib_time = time_algorithm(
                ib_algorithm, graph, timeout=timeout
            )

            difference = (
                rab_result - ib_result
                if isinstance(rab_result, (int, float)) and isinstance(ib_result, (int, float))
                else None
            )

            print(f"  → {algorithm_name(rab_algorithm)}: {rab_result} ({rab_time}s)")
            print(f"  → {algorithm_name(ib_algorithm)}: {ib_result} ({ib_time}s)")
            print(f"  → Optimal: {optimal_value}")
            print(f"  → Difference: {difference}")

            # --- Write row ---
            writer.writerow([
                dataset_category,
                dataset_name,
                graph.number_of_nodes(),
                graph.number_of_edges(),                  
                algorithm_name(rab_algorithm),
                algorithm_name(ib_algorithm),
                rab_result,
                ib_result,
                optimal_value,
                difference,
                rab_time,
                ib_time
            ])

    print(f"\n✅ Finished evaluating all datasets. Results saved to: {output_path}")
    print(f"Timed out on {timed_out}")






class TimeoutException(Exception):
    """Raised when an algorithm exceeds the time limit."""
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException()


def run_algorithm_with_timeout(algorithm, graph, timeout=45):
    """Run algorithm(graph) with a timeout; return result or None if timed out."""
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)

    try:
        return algorithm(graph)
    except TimeoutException:
        # Disable alarm immediately to avoid race conditions
        signal.alarm(0)
        print(f"\t⚠️ Timed out after {timeout} seconds")
        return None
    except Exception as e:
        print("\n❌ Error running algorithm:")
        print(f"  • Exception Type: {type(e).__name__}")
        print(f"  • Message: {e}")
        print("  • Traceback:")
        traceback.print_exc()
        return None
    finally:
        # Disable any leftover alarms once more as safety
        try:
            signal.alarm(0)
        except Exception:
            pass


def algorithm_description(algorithm):
    """
    Returns a clean CSV-safe title derived from an algorithm's __name__.
    Removes the base algorithm and formats its parameters clearly.
    """
    description = []
    configurations = algorithm.config
    for key, value in configurations.items():
        description.append(f"{key}: {value}")
    
    return description



import csv, os


def compare_to_optimal(csv_path, optimal_cover_sizes, delimiter="\t"):
    """
    Compares algorithm bounds in a CSV file to known optimal clique cover sizes.
    """
    comparisons = []

    with open(csv_path, "r", newline="") as f:
        # --- Skip the first algorithm description line ---
        first_line = f.readline().strip()
        if "reductions" in first_line and "heuristic" in first_line:
            print(f"(Skipping config header: {first_line})")

        # --- Now start the real CSV reader ---
        reader = csv.DictReader(f, delimiter=delimiter)

        print(f"\n=== Comparing results in {csv_path} ===\n")
        print(f"{'Dataset':25} {'Optimal':>10} {'RAB':>10} {'IB':>10} {'ΔRAB':>10} {'ΔIB':>10}")
        print("-" * 70)

        for row in reader:
            raw_name = row.get("dataset_name", "").strip()
            if not raw_name:
                continue

            dataset = os.path.splitext(raw_name)[0]  # remove .txt etc.

            # --- Skip if no known optimal ---
            if dataset not in optimal_cover_sizes:
                continue

            try:
                optimal = int(optimal_cover_sizes[dataset])
                rab = float(row["reduce_and_bound"])
                ib = float(row["independence_bound"])
            except (KeyError, ValueError):
                continue

            diff_rab = rab - optimal
            diff_ib = ib - optimal

            comparisons.append({
                "dataset": dataset,
                "optimal": optimal,
                "reduce_and_bound": rab,
                "independence_bound": ib,
                "diff_rab": diff_rab,
                "diff_ib": diff_ib
            })

            print(f"{dataset:25} {optimal:10} {rab:10.0f} {ib:10.0f} {diff_rab:10.0f} {diff_ib:10.0f}")

    print(f"\n✅ Compared {len(comparisons)} datasets with known optimal values.\n")
    return comparisons




if __name__ == "__main__":
    # Example usage:
    # You can choose any dataset subset, e.g. small_datasets, large_datasets, or a custom list.
    datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()


    non_testing_datasets = [dataset for dataset in datasets if dataset not in test_datasets]

    # Run on a subset (for example, the small datasets)
    evaluate_bounds_on_datasets(non_testing_datasets, output_path="all_dataset_bounds.csv", timeout=5)



