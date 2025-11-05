from tools import *
from heuristics import randomized_construction
import copy


def solve(customers, vehicles, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best"):

    best_solution = copy.deepcopy(vehicles)
    randomized_construction.solve(customers, best_solution, to_fulfilled, rho) # initialize best solution

    while True:
        neighborhood = compute_neighborhood(customers, best_solution, neighborhood_structure)
        current_solution = select_neighbor(best_solution, neighborhood, improvement_strategy, rho)

        if current_solution is None:
            break
        else:
            best_solution = current_solution

    # write new solution into vehicles
    for old_vehicle, new_vehicle in zip(vehicles, best_solution):
        old_vehicle.replace(new_vehicle)



def compute_neighborhood(customers, solution, neighborhood_structure):
    if neighborhood_structure == "exchange":
        neighborhood = compute_exchange_neighborhood(customers, solution)
    #elif neighborhood_structure == "2":
    #    neighborhood =
    #elif neighborhood_structure == "3":
    #    neighborhood =
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")

    return neighborhood

def compute_exchange_neighborhood(customers, solution):
    neighborhood = []

    for i, customer_i in enumerate(customers):
        for j, customer_j in enumerate(customers):
            if i >= j:
                continue  # avoid duplicates

            # Find the vehicles these customers currently belong to
            vehicle_i = find_vehicle(solution, customer_i.pickup)
            vehicle_j = find_vehicle(solution, customer_j.pickup)

            # Intra-route swap (both customers in same vehicle)
            if vehicle_i == vehicle_j:
                neighbor = copy.deepcopy(solution)
                v = neighbor[vehicle_i.index]
                swap_pair_in_vehicle(v, customer_i, customer_j)
                if is_valid(v):
                    neighborhood.append(neighbor)

            # Inter-route swap (customers in different vehicles)
            else:
                neighbor = copy.deepcopy(solution)
                v_i = neighbor[vehicle_i.index]
                v_j = neighbor[vehicle_j.index]
                swap_pairs_between_vehicles(v_i, v_j, customer_i, customer_j)
                if is_valid(v_i) and is_valid(v_j):
                    neighborhood.append(neighbor)

    return neighborhood


def is_valid(vehicle):
    for load in vehicle.loads:
        if load > vehicle.capacity:
            return False
    return True

def swap_pair_in_vehicle(vehicle, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    path = vehicle.path
    for k in range(len(path)):
        if path[k] == p_a:
            path[k] = p_b
        elif path[k] == d_a:
            path[k] = d_b
        elif path[k] == p_b:
            path[k] = p_a
        elif path[k] == d_b:
            path[k] = d_a
    vehicle.path = path

def swap_pairs_between_vehicles(v1, v2, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    v1.replace_point(p_a, p_b, cust_b.goods)
    v2.replace_point(p_b, p_a, cust_a.goods)
    v1.replace_point(d_a, d_b, (-1) * cust_b.goods)
    v2.replace_point(d_b, d_a, (-1) * cust_a.goods)



def select_neighbor(best_solution, neighborhood, improvement_strategy, rho):
    if improvement_strategy == "first":
        neighbor = first_improvement(best_solution, neighborhood, rho)
    elif improvement_strategy == "best":
        neighbor = best_improvement(best_solution, neighborhood, rho)
    else:
        raise ValueError(f"Unknown improvement strategy: {improvement_strategy}")
    return neighbor


def first_improvement(best_solution, neighborhood, rho):
    for neighbor in neighborhood:
        if objective_function(neighbor, rho) < objective_function(best_solution, rho):
            return neighbor
    return None

def best_improvement(best_solution, neighborhood, rho):
    best = None
    best_value = objective_function(best_solution, rho)

    for neighbor in neighborhood:
        val = objective_function(neighbor, rho)
        if val < best_value:
            best = neighbor
            best_value = val

    return best