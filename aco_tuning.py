import random
import numpy as np
import os
from itertools import product
import numpy as np
from scipy.stats import friedmanchisquare, wilcoxon
import logging
import csv

from heuristics.ant_colony_optimization import solve
from solve_SCF_PDP import process_for_statistic

RESULTS_CSV = "results/aco_results.csv"

def load_results_cache(csv_path=RESULTS_CSV):
    cache = {}

    if not os.path.exists(csv_path):
        return cache

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

        if not rows:
            return cache

        # Detect header
        has_header = rows[0][0] == "n_colonies"

        data_rows = rows[1:] if has_header else rows

        for row in data_rows:
            try:
                key = (
                    int(row[0]),     # n_colonies
                    float(row[1]),   # alpha
                    float(row[2]),   # beta
                    float(row[3]),   # evaporation
                    row[4]           # instance
                )
                cache[key] = float(row[5])  # value
            except (IndexError, ValueError):
                continue

    return cache


def append_result_to_csv(cfg, instance_path, value, csv_path=RESULTS_CSV):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "n_colonies", "alpha", "beta", "evaporation",
                "instance", "value"
            ])

        writer.writerow([
            cfg[0], cfg[1], cfg[2], cfg[3],
            os.path.basename(instance_path),
            value
        ])

def setup_logger(log_file="logs/aco_race.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a"),
            logging.StreamHandler()
        ]
    )

def load_instance_paths(root_dir): 
    instance_files = [] 
    
    if os.path.isdir(root_dir): 
        for file_name in sorted(f for f in os.listdir(root_dir) if f.endswith('.txt')): 
            file_path = os.path.join(root_dir, file_name) 
            instance_files.append(file_path)
            
    return sorted(instance_files)

def build_aco_parameter_space():
    return list(product(
        [5, 10, 20],          # n_colonies
        np.arange(0.5, 3.1, 0.5), # alpha
        np.arange(2.0, 6.1, 1.0), # beta
        np.arange(0.02, 0.21, 0.04)  # evaporation
        # [5],          # n_colonies
        # np.arange(1, 3.1, 1.5), # alpha
        # np.arange(1.0, 4.1, 3), # beta
        # np.arange(0.02, 0.21, 0.2)  # evaporation
    ))

def evaluate_cfg_on_instance(cfg, instance_path, cache, runs=2):
    instance_name = os.path.basename(instance_path)
    key = (cfg[0], cfg[1], cfg[2], cfg[3], instance_name)

    if key in cache:
        logging.info(
            "Cached result found | %s | cfg=%s",
            instance_name, cfg
        )
        return cache[key]

    logging.info(
        "Running ACO | %s | cfg=%s",
        instance_name, cfg
    )

    values = []
    for _ in range(runs):
        obj, _, _ = process_for_statistic(
            "aco", instance_path, None, None, None, cfg
        )
        print(f"obj: {obj}")
        values.append(obj)

    mean_value = float(np.mean(values))

    append_result_to_csv(cfg, instance_path, mean_value)
    cache[key] = mean_value  # update in-memory cache

    return mean_value


def eliminate_by_wilcoxon(results, surviving, alpha):
    """
    Non-parametric elimination using paired Wilcoxon tests
    """

    # Use mean (or median) only for ranking, NOT for inference
    means = {cfg: np.mean(results[cfg]) for cfg in surviving}
    best_cfg = min(means, key=means.get)

    still_surviving = [best_cfg]

    m = len(surviving) - 1  # number of pairwise tests

    for cfg in surviving:
        if cfg == best_cfg:
            continue

        a = results[best_cfg]
        b = results[cfg]

        if len(a) < 2:
            still_surviving.append(cfg)
            continue

        try:
            _, p_value = wilcoxon(a, b, alternative="less")
        except ValueError:
            still_surviving.append(cfg)
            continue

        # Bonferroni correction
        print(f"p_value: {p_value}")
        if p_value >= alpha:
            still_surviving.append(cfg)

    return still_surviving

def aco_race_instances(configs, instance_paths, runs=2, alpha=0.05):
    results = {cfg: [] for cfg in configs}
    surviving = list(configs)

    cache = load_results_cache()

    for i, instance in enumerate(instance_paths, start=1):
        logging.info("Evaluating instance %d / %d", i, len(instance_paths))

        for j, cfg in enumerate(surviving):
            print(f"Evaluating config {j+1} / {len(surviving)}")
            value = evaluate_cfg_on_instance(cfg, instance, cache, runs)
            results[cfg].append(value)

        if len(results[surviving[0]]) <= 2:
            continue

        stat, p_value = friedmanchisquare(
            *[results[cfg] for cfg in surviving]
        )

        if p_value < alpha:
            prev = len(surviving)
            surviving = eliminate_by_wilcoxon(results, surviving, alpha)
            logging.info(
                "Instance %d | survivors: %d (eliminated %d)",
                i, len(surviving), prev - len(surviving)
            )

        if len(surviving) == 1:
            break

    return surviving, results

def start_aco_tuning_instances():
    INSTANCE_DIR = "instances/50/train"
    instance_paths = load_instance_paths(INSTANCE_DIR)
    Theta = build_aco_parameter_space()
    print(len(Theta))

    best_cfgs, results = aco_race_instances(configs=Theta,instance_paths=instance_paths, runs=1, alpha=0.05)

    logging.info("Best configuration(s):")
    for cfg in best_cfgs:
        logging.info(
            "n_colonies=%d, alpha=%.2f, beta=%.2f, evaporation=%.2f",
            cfg[0], cfg[1], cfg[2], cfg[3]
        )

    return best_cfgs, results

def main():
    setup_logger()
    start_aco_tuning_instances()

if __name__ == "__main__":
    main()
