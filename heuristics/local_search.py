import time
from copy import deepcopy

from tools import *
from heuristics import randomized_construction
from heuristics import construction
import copy
from classes.ObjectiveTracker import ObjectiveTracker
from classes import Vehicle


def solve(customers, vehicles, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best"):
    best_solution = copy.deepcopy(vehicles)
    best_solution = randomized_construction.solve(customers, best_solution, to_fulfilled, rho) # initialize best solution
    #best_solution = construction.solve(customers, best_solution, to_fulfilled, rho)

    print(f"objective value of first solution: {objective_function(best_solution, rho)}")

    while True:
        #neighborhood = compute_neighborhood(customers, best_solution, neighborhood_structure, to_fulfilled)
        #current_solution = select_neighbor(best_solution, neighborhood, improvement_strategy, rho)
        current_solution = choose_neighbor(best_solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho)

        if current_solution is None:
            break
        else:
            best_solution = current_solution
            print(f"objective value of better solution: {objective_function(best_solution, rho)}")

    print(best_solution)


    return best_solution

def choose_neighbor(solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho):
    tracker = ObjectiveTracker(solution, rho)
    if improvement_strategy != "first" and improvement_strategy != "best":
        raise ValueError(f"Unknown improvement strategy: {improvement_strategy}")
    if neighborhood_structure == "exchange":
        neighbor = compute_exchange_neighbor(solution, customers, improvement_strategy, tracker)
    #elif neighborhood_structure == "move":
    #    neighbor = compute_move_neighbor(solution, customers, improvement_strategy, to_fulfilled, rho)
    #elif neighborhood_structure == "remove_and_add":
    #    neighbor = compute_remove_and_add_neighbor(solution, customers, improvement_strategy, to_fulfilled, rho)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")
    # TODO: neighborhood with all possible permutations inside a vehicle + combination with exchange
    return neighbor

def test(solution, customers, improvement_strategy, tracker):
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
                    vi_path_length, vj_path_length = predict_new_path_lengths_after_inter_swap(vehicle_i, vehicle_j,customer_i, customer_j)
                    print(vi_path_length==v_i.path_length)

            # only points of customer_j are in a vehicle path
            elif vehicle_i is None and vehicle_j is not None:
                neighbor = copy.deepcopy(solution)
                v_j = neighbor[vehicle_j.index]
                swap_pairs_between_vehicles(None, v_j, customer_i, customer_j)
                if is_valid(v_j):
                    vi_path_length, vj_path_length = predict_new_path_lengths_after_inter_swap(vehicle_i, vehicle_j, customer_i, customer_j)
                    print(vj_path_length == v_j.path_length)

            # Intra-route swap
            elif vehicle_i == vehicle_j:
                neighbor = copy.deepcopy(solution)
                v = neighbor[vehicle_i.index]
                swap_pair_in_vehicle(v, customer_i, customer_j)
                if is_valid(v):
                    path_length = predict_new_path_length_after_intra_swap(vehicle_i, customer_i, customer_j)
                    print(path_length == v.path_length)

            # Inter-route swap
            else:
                neighbor = copy.deepcopy(solution)
                v_i = neighbor[vehicle_i.index]
                v_j = neighbor[vehicle_j.index]
                swap_pairs_between_vehicles(v_i, v_j, customer_i, customer_j)
                if is_valid(v_i) and is_valid(v_j):
                    vi_path_length, vj_path_length = predict_new_path_lengths_after_inter_swap(vehicle_i, vehicle_j, customer_i, customer_j)
                    print(vi_path_length == v_i.path_length)
                    print(vj_path_length == v_j.path_length)



def compute_exchange_neighbor(solution, customers, improvement_strategy, tracker):
    stack = []

    for i, customer_i in enumerate(customers):
        for j, customer_j in enumerate(customers):
            if i >= j:
                continue  # avoid duplicates

            vehicle_i = find_vehicle(solution, customer_i.pickup)
            vehicle_j = find_vehicle(solution, customer_j.pickup)

            # both points are in no vehicle path
            if vehicle_i is None and vehicle_j is None:
                continue
            elif vehicle_i != vehicle_j:
                vi_path_length, vj_path_length = predict_new_path_lengths_after_inter_swap(vehicle_i, vehicle_j, customer_i, customer_j)
                if vi_path_length is None:
                    current_objective = tracker.predict_objective([vehicle_j.path_length], [vj_path_length])
                elif vj_path_length is None:
                    current_objective = tracker.predict_objective([vehicle_i.path_length], [vi_path_length])
                else:
                    current_objective = tracker.predict_objective([vehicle_i.path_length, vehicle_j.path_length], [vi_path_length, vj_path_length])
                if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                    stack.append([vehicle_i, vehicle_j, customer_i, customer_j, current_objective])
            else:
                path_length = predict_new_path_length_after_intra_swap(vehicle_i, customer_i, customer_j)
                current_objective = tracker.predict_objective([vehicle_i.path_length], [path_length])
                if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                    stack.append([vehicle_i, vehicle_j, customer_i, customer_j, current_objective])

            if improvement_strategy == "first" and stack:
                neighbor = copy.deepcopy(solution)
                v_1, v_2, c_1, c_2, o = stack.pop()
                vehicle_i, vehicle_j = None, None
                if v_1 is not None:
                    vehicle_i = neighbor[v_1.index]
                if v_2 is not None:
                    vehicle_j = neighbor[v_2.index]
                perform_exchange(vehicle_i, vehicle_j, c_1, c_2)
                if v_1 is not None and v_2 is not None and is_valid(v_1) and is_valid(v_2):
                    tracker.update(v_1.path_length, vehicle_i.path_length)
                    tracker.update(v_2.path_length, vehicle_j.path_length)
                    return neighbor

                elif v_1 is not None and v_2 is None and is_valid(v_1):
                    tracker.update(v_1.path_length, vehicle_i.path_length)
                    return neighbor

                elif v_1 is None and v_2 is not None and is_valid(v_2):
                    tracker.update(v_2.path_length, vehicle_j.path_length)
                    return neighbor

    if improvement_strategy == "best" and stack:
        while stack:
            neighbor = copy.deepcopy(solution)
            v_1, v_2, c_1, c_2, o = stack.pop()
            vehicle_i, vehicle_j = None, None
            if v_1 is not None:
                vehicle_i = neighbor[v_1.index]
            if v_2 is not None:
                vehicle_j = neighbor[v_2.index]
            perform_exchange(vehicle_i, vehicle_j, c_1, c_2)
            if v_1 is not None and v_2 is not None and is_valid(v_1) and is_valid(v_2):
                tracker.update(v_1.path_length, vehicle_i.path_length)
                tracker.update(v_2.path_length, vehicle_j.path_length)
                return neighbor

            elif v_1 is not None and v_2 is None and is_valid(v_1):
                tracker.update(v_1.path_length, vehicle_i.path_length)
                return neighbor

            elif v_1 is None and v_2 is not None and is_valid(v_2):
                tracker.update(v_2.path_length, vehicle_j.path_length)
                return neighbor
    return None

def perform_exchange(vehicle_i, vehicle_j, customer_i, customer_j):
    # only points of customer_i are in a vehicle path
    if vehicle_i is not None and vehicle_j is None:
        swap_pairs_between_vehicles(vehicle_i, None, customer_i, customer_j)
    # only points of customer_j are in a vehicle path
    elif vehicle_i is None and vehicle_j is not None:
        swap_pairs_between_vehicles(None, vehicle_j, customer_i, customer_j)
    # Intra-route swap
    elif vehicle_i == vehicle_j:
        swap_pair_in_vehicle(vehicle_i, customer_i, customer_j)
    # Inter-route swap
    else:
        swap_pairs_between_vehicles(vehicle_i, vehicle_j, customer_i, customer_j)


def predict_new_path_length_after_intra_swap(vehicle, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    length = vehicle.path_length

    path = vehicle.path

    first_visit = min([p_a, p_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == p_a:
        path, length = vehicle.predict_path_after_remove(p_a, path, length)
        path, length = vehicle.predict_path_after_replace(p_b, p_a, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, p_b, path, length)
    elif first_visit == p_b:
        path, length = vehicle.predict_path_after_remove(p_b, path, length)
        path, length = vehicle.predict_path_after_replace(p_a, p_b, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, p_a, path, length)

    first_visit = min([d_a, d_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == d_a:
        path, length = vehicle.predict_path_after_remove(d_a, path, length)
        path, length = vehicle.predict_path_after_replace(d_b, d_a, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, d_b, path, length)
    elif first_visit == d_b:
        path, length = vehicle.predict_path_after_remove(d_b, path, length)
        path, length = vehicle.predict_path_after_replace(d_a, d_b, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, d_a, path, length)

    return length

def predict_new_path_lengths_after_inter_swap(v1, v2, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    v1_path_length, v2_path_length = None, None

    if v1 is not None:
        v1_path_length = v1.path_length
        path = v1.path
        path, v1_path_length_1 = v1.predict_path_after_replace(p_a, p_b, path, v1_path_length)
        path, v1_path_length_2 = v1.predict_path_after_replace(d_a, d_b, path, v1_path_length)
        v1_path_length = v1_path_length_1 + v1_path_length_2 - v1.path_length
    if v2 is not None:
        v2_path_length = v2.path_length
        path = v2.path
        path, v2_path_length_1 = v2.predict_path_after_replace(p_b, p_a, path, v2_path_length)
        path, v2_path_length_2 = v2.predict_path_after_replace(d_b, d_a, path, v2_path_length)
        v2_path_length = v2_path_length_1 + v2_path_length_2 - v2.path_length

    return v1_path_length, v2_path_length

def swap_pair_in_vehicle(vehicle, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    path = vehicle.path

    first_visit = min([p_a, p_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == p_a:
        vehicle.remove_section_path(p_a)
        vehicle.replace_point(p_b, p_a)
        vehicle.add_section_path_after(pred, p_b)
    elif first_visit == p_b:
        vehicle.remove_section_path(p_b)
        vehicle.replace_point(p_a, p_b)
        vehicle.add_section_path_after(pred, p_a)

    first_visit = min([d_a, d_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == d_a:
        vehicle.remove_section_path(d_a)
        vehicle.replace_point(d_b, d_a)
        vehicle.add_section_path_after(pred, d_b)
    elif first_visit == d_b:
        vehicle.remove_section_path(d_b)
        vehicle.replace_point(d_a, d_b)
        vehicle.add_section_path_after(pred, d_a)

def swap_pairs_between_vehicles(v1, v2, cust_a, cust_b):
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    if v1 is not None:
        v1.replace_point(p_a, p_b)
        v1.replace_point(d_a, d_b)
    if v2 is not None:
        v2.replace_point(p_b, p_a)
        v2.replace_point(d_b, d_a)


def compute_neighborhood(customers, solution, neighborhood_structure, to_fulfilled):
    if neighborhood_structure == "exchange":
        neighborhood = compute_exchange_neighborhood(customers, solution)
    elif neighborhood_structure == "move":
        neighborhood = compute_move_neighborhood(customers, solution, to_fulfilled)
    elif neighborhood_structure == "remove_and_add":
        neighborhood = compute_remove_and_add_neighborhood(customers, solution, to_fulfilled)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")

    return neighborhood

def compute_intra_move_neighborhood(customers, solution, to_fulfilled):
    neighborhood = []

    for customer in customers:
        vehicle = find_vehicle(solution, customer.pickup)

        if vehicle is not None:
            neighbor = copy.deepcopy(solution)
            v = neighbor[vehicle.index]
            v.remove_section_path(customer.pickup)
            v.remove_section_path(customer.dropoff)
            if is_valid(v) and is_neighbor_valid(neighbor, to_fulfilled):
                neighborhood.append(neighbor) # solution where points are moved to the set of unassigned customers

        # add points to a vehicle path
        for vehicle_target in solution:
            for i in range(0, len(vehicle_target.path) - 1):
                for j in range(i + 1, len(vehicle_target.path) - 1):
                    neighbor_ij = copy.deepcopy(neighbor)
                    v = neighbor_ij[vehicle_target.index]
                    v.add_section_path_after(v.path[i], customer.pickup)
                    v.add_section_path_after(v.path[j], customer.dropoff)
                    if is_valid(v) and is_neighbor_valid(neighbor_ij, to_fulfilled):
                        neighborhood.append(neighbor_ij)

    return neighborhood

def compute_move_neighborhood(customers, solution, to_fulfilled):
    neighborhood = []

    for customer in customers:
        vehicle_source = find_vehicle(solution, customer.pickup)

        neighbor = copy.deepcopy(solution)

        # remove points from a vehicle path
        if vehicle_source is not None:
            v = neighbor[vehicle_source.index]
            v.remove_section_path(customer.pickup)
            v.remove_section_path(customer.dropoff)
            if is_valid(v) and is_neighbor_valid(neighbor, to_fulfilled):
                neighborhood.append(neighbor) # solution where points are moved to the set of unassigned customers

        # add points to a vehicle path
        for vehicle_target in solution:
            for i in range(0, len(vehicle_target.path) - 1):
                for j in range(i + 1, len(vehicle_target.path) - 1):
                    neighbor_ij = copy.deepcopy(neighbor)
                    v = neighbor_ij[vehicle_target.index]
                    v.add_section_path_after(v.path[i], customer.pickup)
                    v.add_section_path_after(v.path[j], customer.dropoff)
                    if is_valid(v) and is_neighbor_valid(neighbor_ij, to_fulfilled):
                        neighborhood.append(neighbor_ij)

    return neighborhood

def compute_remove_and_add_neighborhood(customers, solution, to_fulfilled):
    neighborhood = []

    for customer in customers:
        vehicle_source = find_vehicle(solution, customer.pickup)

        neighbor = copy.deepcopy(solution)

        # remove points from a vehicle path
        if vehicle_source is not None:
            vehicle = neighbor[vehicle_source.index]
            vehicle.remove_section_path(customer.pickup)
            vehicle.remove_section_path(customer.dropoff)

            for c in customers:
                if c == customer or find_vehicle(solution, c.pickup) is not None:
                    continue
                unfulfilled_customer = c
                for i in range(0, len(vehicle.path) - 1):
                    for j in range(i + 1, len(vehicle.path) - 1):
                        neighbor_ij = copy.deepcopy(neighbor)
                        v = neighbor_ij[vehicle.index]
                        v.add_section_path_after(v.path[i], customer.pickup)
                        v.add_section_path_after(v.path[j], customer.dropoff)
                        if is_valid(v) and is_neighbor_valid(neighbor_ij, to_fulfilled):
                            neighborhood.append(neighbor_ij)

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

def is_neighbor_valid(neighbor, to_fulfilled):
    fulfilled = 0
    for vehicle in neighbor:
        fulfilled = fulfilled + len(vehicle.path)/2
    return fulfilled >= to_fulfilled