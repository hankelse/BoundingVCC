

# from graph import Graph
from data_io.process_data import get_graphs
from algorithms.degeneracy import get_degeneracy
import time
import csv
from concurrent.futures import ProcessPoolExecutor, TimeoutError

def c5s_run_and_write(datasets, algorithm, attempt_timeout=45):
    
    
    header = ["Dataset", "Nodes", "Edges", "Average Degree", "Degeneracy", "C5s Found", "Runtime"]
    csv_rows = [header]
    _datasets, test_datasets, small_datasets, large_datasets, graph_load_fn_map = get_graphs()


    for dir, dataset in datasets:
        print(f"\nCollecting data for {dataset}")

        # Build graph object
        graph = graph_load_fn_map[(dir, dataset)]()

        # Record Nodes and Edges
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()

        # Report nodes and edges to user
        print(f"\tGraph has {num_nodes} nodes and {num_edges} edges")

        # Manually skip graph if too many edges or node
        if num_nodes > 100000 or num_edges > 500000:
            print("\t Manual Check triggered: Skipping this one.")
            continue

        # Calculate average degree
        avg_degree = sum(dict(graph.nx_graph().degree()).values()) / num_nodes
        print(f"\tCalculated avg degree={avg_degree}")

        # Calculate degeneracy
        _, degeneracy = get_degeneracy(graph)
        print(f"\tCalculated degeneracy={degeneracy}")

        # Start Timer
        start = time.perf_counter()
        # Run algo with timeout
        c5s = run_algorithm_with_timeout(algorithm, graph, timeout=attempt_timeout)
        if c5s == None: continue

        # End Timer
        end = time.perf_counter()

        # Get Results
        runtime = end - start
        num_c5s = len(c5s)

        # Report to user
        print(f"\tCollected data: {num_c5s} c5s in {runtime} seconds")

        # Append to rows
        row = [dataset, num_nodes, num_edges, avg_degree, degeneracy, num_c5s, runtime]
        csv_rows.append(row)
    
    print("Writing to csv file...")
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerows(csv_rows)
    
    print("Done.")


import signal

class TimeoutException(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutException()


def run_algorithm_with_timeout(algorithm, graph, timeout=45):
    """Run algorithm(graph) with a timeout, return result or None if timed out."""
    # Register the signal function handler
    signal.signal(signal.SIGALRM, _timeout_handler)
    # Schedule the alarm
    signal.alarm(timeout)

    try:
        return algorithm(graph)
    except TimeoutException:
        print(f"\tTimed out after {timeout} seconds")
        return None
    finally:
        # Disable the alarm
        signal.alarm(0)