from fontTools.misc.bezierTools import epsilon

from classes.Statistic import Statistic
from tools import *
from heuristics import randomized_construction
import copy
import classes.Individual as Individual
import numpy as np



def solve(customers, vehicles, to_fulfilled, rho, population_size=10, s=1.5, selection_method="roulette-wheel", recombination_method="", mutation_method="", num_elites=0, offsprings_per_parent_pair=1, output_statistic=False):

    if num_elites > population_size or num_elites < 0:
        raise ValueError(f"num_elites must be between 0 and population_size ({population_size}): {num_elites}")
    if population_size % offsprings_per_parent_pair != 0 or offsprings_per_parent_pair < 1:
        raise ValueError(f"offsprings_per_parent_pair must be larger than 0 and population_size must be divisible by it: {num_elites}")

    t = 0
    current_population = initialize(customers, vehicles, to_fulfilled, rho, population_size)
    evaluate(current_population, rho, s)
    best = best_individual(current_population)
    while t < 100:
        t += 1
        Q_s = select(current_population, selection_method, offsprings_per_parent_pair, num_elites)
        Q_r = recombine(Q_s, offsprings_per_parent_pair)
        Q_m = mutate(Q_r)

        current_population = replace(current_population, Q_m)
        evaluate(current_population, rho)
        candidate = best_individual(current_population)
        if candidate.cost < best.cost:
            best = candidate

    return best.solution


def evaluate(population, rho, s):
    for ind in population:
        if ind.cost is None:
            ind.cost = objective_function(ind, rho)

    c_max = max(ind.cost for ind in population) + 1
    for ind in population:
        ind.fitness = c_max - ind.cost

    f_avg = sum(ind.fitness for ind in population) / len(population)
    f_max = max(ind.fitness for ind in population)

    # linear scaling
    if f_max != f_avg:
        a = (s * f_avg - f_avg) / (f_max - f_avg)
        b = a * f_avg - f_avg
    else:
        a = 1.0
        b = 0.0

    for ind in population:
        ind.fitness = a * ind.fitness + b


def initialize(customers, vehicles, to_fulfilled, rho, population_size):
    new_population = []
    for i in range(population_size):
        individual = Individual.Individual()
        individual.solution = randomized_construction.solve(customers, copy.deepcopy(vehicles), to_fulfilled, rho, strategy="with_reordering", alpha=1)
        new_population.append(individual)
    return new_population


def best_individual(population):
    best = None
    for ind in population:
        if best is None or best.cost > ind.cost:
            best = ind
    return best


def select(current_population, selection_method, offsprings_per_parent_pair, num_elites):
    if selection_method == "roulette-wheel":
        selection = roulette_wheel_selection(current_population, 2 * (len(current_population) - num_elites) / offsprings_per_parent_pair)
    else:
        raise ValueError(f"Unknown selection method: {selection_method}")
    return selection


def roulette_wheel_selection(population, num_parents):
    fitnesses = np.array([ind.fitness for ind in population])
    probabilities = fitnesses / fitnesses.sum()
    indices = np.random.choice(len(population), size=num_parents, p=probabilities)
    return [population[i] for i in indices]


def recombine(Q_s):
    pass


def mutate(Q_r):
    pass


def replace(current_population, Q_m):
    pass