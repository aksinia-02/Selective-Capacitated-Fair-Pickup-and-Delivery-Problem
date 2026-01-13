import random

from classes.ObjectiveTracker import ObjectiveTracker
from classes.Statistic import Statistic
from heuristics.neighborhood_structures.neighborhood_utils import predict_new_path_lengths_after_move
from tools import *
from heuristics import randomized_construction
import copy
import classes.Individual as Individual
import numpy as np
from heuristics.neighborhood_structures.exchange_neighborhood import perform_exchange
from heuristics.neighborhood_structures.move_neighborhood import perform_move
from heuristics.neighborhood_structures.neighborhood_core import choose_neighbor

def solve(customers, vehicles, to_fulfilled, rho, t_max=80, population_size=20, s=1.3968, selection_method="tournament", tournament_size=18, tournament_replace=True, recombination_weights=None, mutation_weights=None, num_elites=0, recombination_samples=125, recombination_rate=0.4202, mutation_rate=0.5943, output_statistic=False):
    if s < 1 or s > 2:
        raise ValueError(f"s must be between 1 and 2: {s}")
    if num_elites > population_size or num_elites < 0:
        raise ValueError(f"num_elites must be between 0 and population_size ({population_size}): {num_elites}")
    if tournament_size > population_size or tournament_size < 0:
        raise ValueError(f"tournament_size must be between 0 and population_size ({population_size}): {tournament_size}")
    if recombination_samples < 10 or recombination_samples > 1000:
        raise ValueError(f"recombination_samples must be between 10 and 1000: {recombination_samples}")
    if recombination_rate < 0 or recombination_rate > 1:
        raise ValueError(f"recombination_rate must be between 0 and 1: {recombination_rate}")
    if mutation_rate < 0 or mutation_rate > 1:
        raise ValueError(f"mutation_rate must be between 0 and 1: {mutation_rate}")
    if recombination_weights is None:
        recombination_weights = [0.9446, 0.4373]
    else:
        if len(recombination_weights) != len(RECOMBINATION_METHODS):
            raise ValueError(
                f"Expected exactly {len(RECOMBINATION_METHODS)} recombination weights, got {len(recombination_weights)}"
            )
    if mutation_weights is None:
        mutation_weights = [0.0919,0.5, 0.1860]
    else:
        if len(mutation_weights) != len(MUTATION_METHODS):
            raise ValueError(
                f"Expected exactly {len(MUTATION_METHODS)} mutation weights, got {len(mutation_weights)}"
            )

    t = 0
    current_population = initialize(customers, vehicles, to_fulfilled, rho, population_size)
    evaluate(current_population, rho, s)
    best = best_individual(current_population)
    statistic = Statistic(best.solution, rho)

    while t < t_max:
        print("iteration: ", t)
        t += 1
        Q_s = select(current_population, selection_method, num_elites, tournament_size, tournament_replace)
        Q_r = recombine(Q_s, recombination_rate, recombination_weights, customers, to_fulfilled, rho, recombination_samples)
        Q_m = mutate(Q_r, mutation_rate, mutation_weights, customers, to_fulfilled, rho)

        current_population = replace(current_population, Q_m, num_elites)
        evaluate(current_population, rho, s)
        candidate = best_individual(current_population)
        #candidate.solution = variable_neighborhood_descent.solve(customers, candidate.solution, to_fulfilled, rho, improvement_strategy="first")
        statistic.update(candidate.solution, rho)
        if candidate.cost < best.cost:
            print("new best solution with obj: ", candidate.cost)
            best = candidate

    #best.solution = variable_neighborhood_descent.solve(customers, best.solution, to_fulfilled, rho, improvement_strategy="first")
    if output_statistic:
        return best.solution, statistic
    else:
        print(best.solution)
        return best.solution



def evaluate(population, rho, s):
    for ind in population:
        ind.cost = objective_function(ind.solution, rho)

    c_max = max(ind.cost for ind in population) + 1
    for ind in population:
        ind.fitness = c_max - ind.cost

    f_avg = sum(ind.fitness for ind in population) / len(population)
    f_max = max(ind.fitness for ind in population)
    g_min = min(ind.fitness for ind in population)

    # linear scaling
    if f_max != f_avg:
        a = (s * f_avg - f_avg) / (f_max - f_avg)
        b = a * f_avg - f_avg
    else:
        a = 1.0
        b = 0.0

    if a * g_min + b < 0:
        a = f_avg / (f_avg - g_min)
        b = a * f_avg - f_avg

    for ind in population:
        ind.fitness = a * ind.fitness + b


def initialize(customers, vehicles, to_fulfilled, rho, population_size):
    new_population = []

    for _ in range(population_size):
        individual = Individual.Individual()

        solution = copy.deepcopy(vehicles)

        for v in solution:
            depot = v.path[0]
            v.path = [depot, depot]
            v.path_length = 0
            v.load = 0
            v.load_history = [0, 0]

        for customer in customers:
            v = random.choice(solution)
            v.add_section_path_before(v.path[-1], copy.deepcopy(customer.pickup))
            v.add_section_path_before(v.path[-1], copy.deepcopy(customer.dropoff))

        for i, v in enumerate(solution):
            v.index = i

        individual.solution = solution
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


def recombine(Q_s, recombination_rate, recombination_weights, customers, to_fulfilled, rho, samples):
    offsprings = []
    n = len(Q_s)
    i = 0

    while i < n - 1:
        parent1 = Q_s[i]
        parent2 = Q_s[i+1]

        if random.random() < recombination_rate:
            recombination = random.choices(
                RECOMBINATION_METHODS,
                weights=recombination_weights,
                k=1
            )[0]
            children = recombination(parent1, parent2, customers, to_fulfilled, rho, samples)
            if len(children) == 1:
                children.extend(recombination(parent2, parent1, customers, to_fulfilled, rho, samples))
        else:
            children = [copy.deepcopy(parent1), copy.deepcopy(parent2)]

        offsprings.extend(children)
        i += 2

    if n % 2 == 1:
        last_parent = Q_s[-1]
        offsprings.append(copy.deepcopy(last_parent))

    return offsprings

def get_order_from_parent(parent, customers):
    order = []
    seen = set()
    for v in parent.solution:
        for node in v.path:
            for c in customers:
                if node == c.pickup or node == c.dropoff:
                    if c not in seen:
                        seen.add(c)
                        order.append(c)
    return order

def customer_based_recombination(parent1, parent2, customers, to_fulfilled, rho, samples):
    child = copy.deepcopy(parent1)

    keep = set()
    for c in customers:
        if random.random() < 0.8:
            keep.add(c)

    for c in customers:
        if c not in keep:
            v = find_vehicle(child.solution, c.pickup)
            if v is not None:
                v.remove_section_path(c.pickup)
                v.remove_section_path(c.dropoff)

    order = get_order_from_parent(parent2, customers)
    missing = [c for c in order if c not in keep]

    for customer in missing:
        vehicle = find_vehicle(parent2.solution, customer.pickup)
        if vehicle is None:
            shortest_path = None
            shortest_vehicle = None
            for vehicle in child.solution:
                if shortest_path is None or shortest_path > vehicle.path_length:
                    shortest_path = vehicle.path_length
                    shortest_vehicle = vehicle
            stochastic_insertion(child.solution, shortest_vehicle, customer, rho, customers, samples)

        else:
            stochastic_insertion(child.solution, child.solution[vehicle.index], customer, rho, customers, samples)

    repair_child(child.solution, parent1.solution, parent2.solution, customers, to_fulfilled, rho, samples)

    return [child]

def vehicle_based_recombination(parent1, parent2, customers, to_fulfilled, rho, samples):
    child1 = copy.deepcopy(parent1)
    child2 = copy.deepcopy(parent2)

    random.shuffle(child1.solution)

    for i, vehicle in enumerate(child1.solution):
        vehicle.index = i

    for k in range(len(child1.solution)):
        if random.random() < 0.5:
            child1.solution[k], child2.solution[k] = child2.solution[k], child1.solution[k]

    repair_child(child1.solution, parent1.solution, parent2.solution, customers, to_fulfilled, rho, samples)
    repair_child(child2.solution, parent1.solution, parent2.solution, customers, to_fulfilled, rho, samples)

    return [child1, child2]

def stochastic_insertion(solution, destination_vehicle, customer, rho, customers, samples):
    path = destination_vehicle.path
    n = len(path)

    if n < 2:
        return

    if n == 2:
        destination_vehicle.add_section_path_before(destination_vehicle.path[-1], customer.pickup)
        destination_vehicle.add_section_path_before(destination_vehicle.path[-1], customer.dropoff)
        return

    tracker = ObjectiveTracker(solution, rho)

    best_list = []
    tried = set()

    attempts = 0
    max_attempts = samples * 5

    while len(best_list) < samples and attempts < max_attempts:
        attempts += 1

        i = random.randrange(0, n-1)
        j = random.randrange(i+1, n)

        if (i, j) in tried:
            continue
        tried.add((i, j))

        _, new_len = predict_new_path_lengths_after_move(
            None,
            destination_vehicle,
            customer,
            path[i],
            path[j]
        )

        obj = tracker.predict_objective(
            [destination_vehicle.path_length],
            [new_len]
        )

        candidate = [destination_vehicle, customer, i, j, obj]

        inserted = False
        for idx in range(len(best_list)):
            if obj < best_list[idx][-1]:
                best_list.insert(idx, candidate)
                inserted = True
                break
        if not inserted:
            best_list.append(candidate)

        if len(best_list) > samples:
            best_list.pop()

    best_list = list(reversed(best_list))

    while best_list:
        destination_vehicle, customer, i, j, _ = best_list.pop()
        perform_move(None, destination_vehicle, customer, path[i], path[j])
        if is_valid(destination_vehicle, customers):
            return
        destination_vehicle.remove_section_path(customer.pickup)
        destination_vehicle.remove_section_path(customer.dropoff)

    destination_vehicle.add_section_path_before(destination_vehicle.path[-1], customer.pickup)
    destination_vehicle.add_section_path_before(destination_vehicle.path[-1], customer.dropoff)
    reorder_paths(solution, len(customers))

def repair_child(child, parent1, parent2, customers, to_fulfilled, rho, samples):

    for customer in customers:
        customer_counter = 0
        v1 = None
        v2 = None
        for v in child:
            if customer.pickup in v.path:
                customer_counter += 1
                if customer_counter == 1:
                    v1 = v
                elif customer_counter == 2:
                    v2 = v

        if v1 is not None and v2 is not None:
            if v1.path_length < v2.path_length:
                v2.remove_section_path(customer.dropoff)
                v2.remove_section_path(customer.pickup)
            else:
                v1.remove_section_path(customer.dropoff)
                v1.remove_section_path(customer.pickup)

    i = 0
    if is_solution_valid(child, to_fulfilled):
        return


    unfulfilled = []
    for customer in customers:
        if find_vehicle(child, customer.pickup) is None:
            unfulfilled.append(customer)

    while not is_solution_valid(child, to_fulfilled) and i < to_fulfilled:
        i = i + 1
        customer = random.choice(unfulfilled)
        unfulfilled.remove(customer)
        shortest_path = None
        shortest_vehicle = None
        for vehicle in child:
            if shortest_path is None or shortest_path > vehicle.path_length:
                shortest_path = vehicle.path_length
                shortest_vehicle = vehicle
        stochastic_insertion(child, shortest_vehicle, customer, rho, customers, samples)




def mutate(Q_r, mutation_rate, mutation_weights, customers, to_fulfilled, rho):
    mutated_population = []

    for ind in Q_r:
        if random.random() < mutation_rate:
            mutation = random.choices(
                MUTATION_METHODS,
                weights=mutation_weights,
                k=1
            )[0]
            mutated_population.append(mutation(ind, customers, to_fulfilled, rho))
        else:
            mutated_population.append(ind)

    return mutated_population

def swap_mutation(individual, customers, _to_fulfilled, _rho, max_attempts=5):
    for _ in range(max_attempts):
        mutated_solution = copy.deepcopy(individual.solution)

        first, second = random.sample(customers, 2)

        first_v = find_vehicle(mutated_solution, first.pickup)
        second_v = find_vehicle(mutated_solution, second.pickup)

        if first_v is None and second_v is None:
            continue
        perform_exchange(first_v, second_v, first, second)

        if (first_v is None or is_valid(first_v, customers)) and \
           (second_v is None or is_valid(second_v, customers)):

            new_individual = copy.deepcopy(individual)
            new_individual.solution = mutated_solution
            return new_individual

    return individual



def move_mutation(individual, customers, _to_fulfilled, _rho, max_attempts=5):
    for _ in range(max_attempts):
        mutated_solution = copy.deepcopy(individual.solution)

        assigned_customers = [
            c for c in customers
            if find_vehicle(mutated_solution, c.pickup) is not None
        ]
        if not assigned_customers:
            return individual

        customer = random.choice(assigned_customers)
        vehicle = find_vehicle(mutated_solution, customer.pickup)

        possible_targets = [v for v in mutated_solution if v is not vehicle]
        if not possible_targets:
            return individual

        target_vehicle = random.choice(possible_targets)

        n = len(target_vehicle.path)
        if n < 3:
            continue

        i = random.randrange(1, n - 1)
        j = random.randrange(i + 1, n)

        perform_move(
            vehicle,
            target_vehicle,
            customer,
            target_vehicle.path[i],
            target_vehicle.path[j]
        )

        if is_valid(vehicle, customers) and is_valid(target_vehicle, customers):
            new_individual = copy.deepcopy(individual)
            new_individual.solution = mutated_solution
            return new_individual

    return individual

def neighborhood_mutation(individual, customers, to_fulfilled, rho, max_attempts=5):
    neighbourhood_structures = ["exchange", "pickup_relocate",
        "dropoff_relocate", "remove_and_append", "move"]
    neighborhood_structure = random.choice(neighbourhood_structures)
    better_solution = choose_neighbor(individual.solution, customers, neighborhood_structure, "first", to_fulfilled, rho)
    if better_solution is not None:
        individual.solution = better_solution
    return individual



def replace(old_population, offsprings, num_elites):

    old_sorted = sorted(old_population, key=lambda ind: ind.cost)
    elites = old_sorted[:num_elites]
    next_population = elites + offsprings

    return next_population

MUTATION_METHODS = [
    swap_mutation,
    move_mutation,
    neighborhood_mutation,
]

RECOMBINATION_METHODS = [
    vehicle_based_recombination,
    customer_based_recombination,
]
