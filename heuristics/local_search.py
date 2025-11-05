from os import remove

from tools import *
from heuristics import randomized_construction
import copy
import math


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

            vehicle_i = find_vehicle(solution, customer_i.pickup)
            vehicle_j = find_vehicle(solution, customer_j.pickup)

            # both points are in no vehicle path
            if vehicle_i is None and vehicle_j is None:
                continue
            # only points of customer_i are in a vehicle path
            elif vehicle_i is not None and vehicle_j is None:
                neighbor = copy.deepcopy(solution)
                v_i = neighbor[vehicle_i.index]
                swap_pairs_between_vehicles(v_i, None, customer_i, customer_j)
                if is_valid(v_i):
                    neighborhood.append(neighbor)
            # only points of customer_j are in a vehicle path
            elif vehicle_i is None and vehicle_j is not None:
                neighbor = copy.deepcopy(solution)
                v_j = neighbor[vehicle_j.index]
                swap_pairs_between_vehicles(None, v_j, customer_i, customer_j)
                if is_valid(v_j):
                    neighborhood.append(neighbor)

            # Intra-route swap
            elif vehicle_i == vehicle_j:
                neighbor = copy.deepcopy(solution)
                v = neighbor[vehicle_i.index]
                swap_pair_in_vehicle(v, customer_i, customer_j)
                if is_valid(v):
                    neighborhood.append(neighbor)

            # Inter-route swap
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

    first_visit = min([p_a, p_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == p_a:
        vehicle.remove_section_path(p_a)
        vehicle.replace_section_path(p_b, p_a, cust_a.goods)
        vehicle.add_section_path_between(pred, p_b, cust_b.goods)
    elif first_visit == p_b:
        vehicle.remove_section_path(p_b)
        vehicle.replace_section_path(p_a, p_b, cust_b.goods)
        vehicle.add_section_path_between(pred, p_a, cust_a.goods)

    first_visit = min([d_a, d_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == d_a:
        vehicle.remove_section_path(d_a)
        vehicle.replace_section_path(d_b, d_a, (-1) * cust_a.goods)
        vehicle.add_section_path_between(pred, d_b, (-1) * cust_b.goods)
    elif first_visit == d_b:
        vehicle.remove_section_path(d_b)
        vehicle.replace_section_path(d_a, d_b, (-1) * cust_b.goods)
        vehicle.add_section_path_between(pred, d_a, (-1) * cust_a.goods)



def swap_pairs_between_vehicles(v1, v2, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    if v1 is not None:
        v1.replace_point(p_a, p_b, cust_b.goods)
        v1.replace_point(d_a, d_b, (-1) * cust_b.goods)
    elif v2 is not None:
        v2.replace_point(p_b, p_a, cust_a.goods)
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