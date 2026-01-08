import random

from classes.Statistic import Statistic
from tools import *
from heuristics import randomized_construction
import copy
import classes.Individual as Individual
import numpy as np



def solve(customers, vehicles, to_fulfilled, rho, population_size=10, s=1.5, selection_method="roulette-wheel", tournament_size=3, tournament_replace=True, recombination_method="", mutation_method="", num_elites=0, output_statistic=False, recombination_rate=1, mutation_rate=0.1):

    if s < 1 or s > 2:
        raise ValueError(f"s must be between 1 and 2: {s}")
    if num_elites > population_size or num_elites < 0:
        raise ValueError(f"num_elites must be between 0 and population_size ({population_size}): {num_elites}")
    if tournament_size > population_size or tournament_size < 0:
        raise ValueError(f"tournament_size must be between 0 and population_size ({population_size}): {tournament_size}")
    if recombination_rate < 0 or recombination_rate > 1:
        raise ValueError(f"recombination_rate must be between 0 and 1: {recombination_rate}")
    if mutation_rate < 0 or mutation_rate > 1:
        raise ValueError(f"mutation_rate must be between 0 and 1: {mutation_rate}")

    t = 0
    current_population = initialize(customers, vehicles, to_fulfilled, rho, population_size)
    evaluate(current_population, rho, s)
    best = best_individual(current_population)
    statistic = Statistic(best.solution, rho)

    while t < 100:
        t += 1
        Q_s = select(current_population, selection_method, num_elites, tournament_size, tournament_replace)
        Q_r = recombine(Q_s, recombination_rate, recombination_method)
        Q_m = mutate(Q_r, mutation_rate, mutation_method)

        current_population = replace(current_population, Q_m, num_elites)
        evaluate(current_population, rho)
        candidate = best_individual(current_population)
        statistic.update(candidate.solution, rho)
        if candidate.cost < best.cost:
            best = candidate

    if output_statistic:
        return best.solution, statistic
    else:
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


def select(current_population, selection_method, num_elites, tournament_size=3, tournament_replace=True):
    num_parents = int(len(current_population) - num_elites)

    if selection_method == "roulette-wheel":
        return roulette_wheel_selection(current_population, num_parents)
    elif selection_method == "tournament":
        return tournament_selection(current_population, num_parents, k=tournament_size, replace=tournament_replace)
    else:
        raise ValueError(f"Unknown selection method: {selection_method}")


def roulette_wheel_selection(population, num_parents):

    fitnesses = np.array([ind.fitness for ind in population], dtype=float)
    total = fitnesses.sum()

    probabilities = fitnesses / total

    indices = np.random.choice(len(population), size=num_parents, p=probabilities)
    return [population[i] for i in indices]


def tournament_selection(population, num_parents, k=3, replace=True):

    n = len(population)
    selected = []
    for _ in range(num_parents):
        if replace:
            contenders_idx = np.random.randint(0, n, size=k)
            contenders = [population[i] for i in contenders_idx]
        else:
            k_eff = min(k, n)
            contenders = list(np.random.choice(population, size=k_eff, replace=False))

        winner = max(contenders, key=lambda ind: ind.fitness)
        selected.append(winner)

    return selected


def recombine(Q_s, recombination_rate, recombination_method):
    offsprings = []
    n = len(Q_s)
    i = 0

    while i < n - 1:
        parent1 = Q_s[i]
        parent2 = Q_s[i+1]

        if random.random() < recombination_rate:
            children = recombination_method(parent1, parent2)
        else:
            children = [parent1.copy(), parent2.copy()]

        offsprings.extend(children)
        i += 2

    if n % 2 == 1:
        last_parent = Q_s[-1]
        offsprings.extend(last_parent)

    return offsprings


def mutate(Q_r, mutation_rate, mutation_method):
    mutated_population = []

    for ind in Q_r:
        if random.random() < mutation_rate:
            mutated = mutation_method(ind)
            mutated_population.append(mutated)
        else:
            mutated_population.append(ind)

    return mutated_population


def replace(old_population, offsprings, num_elites):

    old_sorted = sorted(old_population, key=lambda ind: ind.cost)
    elites = old_sorted[:num_elites]
    next_population = elites + offsprings

    return next_population