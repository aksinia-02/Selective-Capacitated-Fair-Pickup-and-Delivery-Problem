import argparse
import sys
import os

original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

import pygame

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
b_dir = os.path.join(parent_dir, "b")

sys.path.append(parent_dir)

from heuristics.genetic_algorithm import solve
from solve_SCF_PDP import read_input_file
from tools import objective_function


def main():
    args = sys.argv

    scenario_id = args[1]  # usually ignored
    iteration_id = args[2]  # usually ignored
    seed = int(args[3])  # optional, if you want reproducibility
    instance_file = args[4]  # THIS is your instance

    # GA parameters start from argv[5] onward:
    t_max = int(args[5])
    population_size = int(args[6])
    s = float(args[7])
    selection_method = args[8]
    tournament_size = int(args[9])
    tournament_replace = args[10] == "True"
    recomb_w1 = float(args[11])
    recomb_w2 = float(args[12])
    mut_w1 = float(args[13])
    mut_w2 = float(args[14])
    mut_w3 = float(args[15])
    num_elites = int(args[16])
    recombination_samples = int(args[17])
    recombination_rate = float(args[18])
    mutation_rate = float(args[19])

    num_elites = min(population_size, num_elites)
    tournament_size = min(population_size, tournament_size)



    # Normalize recombination weights
    rw_sum = recomb_w1 + recomb_w2
    if rw_sum == 0:
        recombination_weights = [0.5, 0.5]
    else:
        recombination_weights = [
            recomb_w1 / rw_sum,
            recomb_w2 / rw_sum
        ]

    # Normalize mutation weights
    mw_sum = mut_w1 + mut_w2 + mut_w3
    if mw_sum == 0:
        mutation_weights = [1 / 3, 1 / 3, 1 / 3]
    else:
        mutation_weights = [
            mut_w1 / mw_sum,
            mut_w2 / mw_sum,
            mut_w3 / mw_sum
        ]

    to_fulfilled, rho, vehicles, customers = read_input_file(instance_file)

    solution = solve(
        customers=customers,
        vehicles=vehicles,
        to_fulfilled=to_fulfilled,
        rho=rho,
        t_max=t_max,
        population_size=population_size,
        s=s,
        selection_method=selection_method,
        tournament_size=tournament_size,
        tournament_replace=tournament_replace,
        recombination_weights=recombination_weights,
        mutation_weights=mutation_weights,
        num_elites=num_elites,
        recombination_samples=recombination_samples,
        recombination_rate=recombination_rate,
        mutation_rate=mutation_rate,
        output_statistic=False
    )

    sys.stdout.close()
    sys.stdout = original_stdout

    cost = objective_function(solution, rho)
    print(cost)


if __name__ == "__main__":
    main()