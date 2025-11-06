import os
import os

def convert_snap_to_metis(directories, output_suffix="_metis"):
    """
    Converts SNAP-format edge lists into METIS adjacency lists.
    Handles 0- vs 1-indexed graphs automatically and removes duplicate edges.
    """
    for dir_path in directories:
        if not os.path.isdir(dir_path):
            print(f"Skipping {dir_path}: not a directory.")
            continue
        
        output_dir = dir_path.rstrip("/\\") + output_suffix
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nConverting graphs in {dir_path} → {output_dir}")

        for filename in os.listdir(dir_path):
            if not filename.endswith(".txt") and not filename.endswith(".snap"):
                continue

            input_path = os.path.join(dir_path, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".metis")

            edges = set()
            nodes = set()

            with open(input_path, 'r') as f:
                for line in f:
                    if line.startswith("#") or line.strip() == "":
                        continue
                    u, v = map(int, line.split())
                    if u == v:
                        continue  # skip self-loops
                    # store undirected edge canonically
                    edges.add(tuple(sorted((u, v))))
                    nodes.update([u, v])

            if not nodes:
                print(f"  ⚠️ Skipping {filename}: no edges found.")
                continue

            # Handle 0-indexing
            offset = 0 if min(nodes) == 1 else 1
            n = max(nodes) + offset

            adj = [[] for _ in range(n + 1)]
            for u, v in edges:
                u += offset
                v += offset
                adj[u].append(v)
                adj[v].append(u)

            # Remove duplicates & sort
            for i in range(1, n + 1):
                adj[i] = sorted(set(adj[i]))

            m = len(edges)
            with open(output_path, 'w') as out:
                out.write(f"{n} {m}\n")
                for i in range(1, n + 1):
                    out.write(" ".join(map(str, adj[i])) + "\n")

            print(f"  ✔ {filename} → {output_path}")

    print("\n✅ Conversion complete (deduplicated & clean).")


def main():
    base_path = "data"

    # Directories to convert
    directories = [
        os.path.join(base_path, "new_snap_datasets"),
        os.path.join(base_path, "snap_datasets"),
        os.path.join(base_path, "test_datasets")
    ]

    convert_snap_to_metis(directories)


if __name__ == "__main__":
    main()
