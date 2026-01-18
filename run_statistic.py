import os
import pandas as pd
import os
import argparse
from solve_SCF_PDP import process_for_statistic

# python -m venv venv
# .\venv\Scripts\Activate
# pip install -r .\requirements.txt

def load_or_create_dataframe(filename, path):
    columns = ["number", "nreq", "nveh", "to_fulfilled", "rho", "avg_time", "avg_obj_func", "avg_max_min_length", "avg_max_min_fairness", "avg_max_min_customers", "iterations"]
    os.makedirs(path, exist_ok=True)
    path = f"{path}/{filename}"
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"Loaded existing file: {path}")
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)
        print(f"Created new file: {path}")
    return df

def save_results_to_csv(results, filename, path):
    path = f"{path}/{filename}"
    df = pd.DataFrame(results)
    if os.path.exists(path):
        existing = pd.read_csv(path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(path, index=False)
    print(f"Results saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Starts solving for a specific folder with instances.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input folder with data.")
    parser.add_argument("-n", "--number_of_experiments", type=int, required=True,
                        help="Runs each algorithm on each instance multiple times to reduce statistical variance.")
    parser.add_argument("-f", "--folder_names", type=str, required=True, nargs="+",
                        help="Folders names to be chosen to work with.")
    parser.add_argument("-t", "--type", type=str, required=True, choices=['c', 'rc', 'ps', 'ls', 'vnd', 'grasp', 'sa', 'aco', 'ga'],
                        help="Type of heuristic.")
    parser.add_argument("-nh", "--neighborhood", type=str, required=False, choices=['exchange', 'pickup_relocate',
                        'dropoff_relocate', 'remove_and_append', 'move'],
                        help="Neighborhood structure.")
    parser.add_argument("-s", "--strategy", type=str, required=False, choices=['pure', 'with_reordering', 'best', 'first'],
                        help="Strategy for the heuristic.")

    args = parser.parse_args()
    print(args)

    data_folder = args.input
    folder_names = args.folder_names
    n = args.number_of_experiments
    neighborhood = args.neighborhood
    strategy = args.strategy

    if strategy is not None:
        if (args.type not in ['c', 'rc', 'ls', 'vnd'] or (args.type in ['c', 'rc'] and strategy not in ['pure', 'with_reordering'])
                or (args.type in ['ls', 'vnd'] and strategy not in ['best', 'first'])):
            raise ValueError(f"Strategy not valid for heuristic type")
        if neighborhood is not None:
            if args.type not in ['ls']:
                raise ValueError(f"Neighborhood not valid for heuristic type")
            path = f"output/{args.type}/{args.neighborhood}_{args.strategy}"
        else:
            path = f"output/{args.type}/{args.strategy}"
    else:
        if neighborhood is not None:
            if args.type not in ['ls']:
                raise ValueError(f"Neighborhood not valid for heuristic type")
            path = f"output/{args.type}/{args.neighborhood}"
        else:
            path = f"output/{args.type}"

    df = load_or_create_dataframe("output.csv", path)

    folder_file_count = 0
    counter = 0
    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)
        file_count = sum(
            f.endswith('.txt') and os.path.isfile(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
        )
        folder_file_count += file_count

    results = []

    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)

        if os.path.isdir(folder_path):
            for file_name in sorted(f for f in os.listdir(folder_path) if f.endswith('.txt')):
                file_path = os.path.join(folder_path, file_name)

                if os.path.isfile(file_path):
                    file_name_full = f"{data_folder}/{folder_name}/{file_name}"

                    print("--------------------------------------------------------")
                    print("--------------------------------------------------------")
                    print(f"Name of the File: {file_name}")

                    with open(file_name_full, 'r') as f:
                        lines = [line.strip() for line in f if line.strip()]

                    nreq, nveh, C, to_fulfilled = map(int, lines[0].split()[:4])
                    rho = float(lines[0].split()[4])

                    result_dict = {
                        "number": counter + 1,
                        "nreq": nreq,
                        "nveh": nveh,
                        "to_fulfilled": to_fulfilled,
                        "rho": rho
                    }

                    output_path = os.path.join(os.path.dirname(file_path.replace("instances", f"{path}")), file_name)
                    avg_time = avg_obj_func = avg_iterations = avg_max_min_length= avg_max_min_fairness = avg_max_min_customers = 0


                    for i in range(n):
                        obj_func, elapsed_time, statistic, max_min_length, max_min_customers, max_min_fairness = process_for_statistic(args.type, file_name_full, output_path, neighborhood, strategy)
                        avg_iterations += statistic.iterations
                        avg_time += elapsed_time
                        avg_obj_func += obj_func
                        avg_max_min_length += max_min_length
                        avg_max_min_fairness += max_min_fairness
                        avg_max_min_customers += max_min_customers

                        df_run = pd.DataFrame({
                            "Iteration": list(range(len(statistic.objective_over_time))),
                            "Objective": statistic.objective_over_time,
                            "Fairness": statistic.fairness_over_time,
                            "Duration": statistic.duration_over_time
                        })
                        progress_path = f"{os.path.dirname(file_path.replace("instances", f"{path}"))}/progress_over_time/{file_name}_({n}).csv"
                        parent = os.path.dirname(progress_path)
                        os.makedirs(parent, exist_ok=True)
                        df_run.to_csv(progress_path, index=False)

                    avg_time = avg_time / n
                    avg_obj_func = avg_obj_func / n
                    avg_iterations = avg_iterations / n
                    avg_max_min_length = avg_max_min_length / n
                    avg_max_min_fairness = avg_max_min_fairness / n
                    avg_max_min_customers = avg_max_min_customers / n
                    result_dict["avg_time"] = avg_time
                    result_dict["avg_obj_func"] = avg_obj_func
                    result_dict["iterations"] = avg_iterations
                    result_dict["avg_max_min_length"] = avg_max_min_length
                    result_dict["avg_max_min_fairness"] = avg_max_min_fairness
                    result_dict["avg_max_min_customers"] = avg_max_min_customers
                    counter += 1
                    results.append(result_dict)



                    print(f"Statistic: {(counter / folder_file_count) * 100:.2f}%")

    save_results_to_csv(results, f"output.csv", path)


if __name__ == "__main__":
    main()