from tools import *
from heuristics import randomized_construction
import copy


def solve(customers, vehicles, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best"):

    best_solution = copy.deepcopy(vehicles)
    best_solution = randomized_construction.solve(customers, best_solution, to_fulfilled, rho) # initialize best solution

    print(f"objective value of first solution: {objective_function(best_solution, rho)}")

    while True:
        neighborhood = compute_neighborhood(customers, best_solution, neighborhood_structure, to_fulfilled)
        current_solution = select_neighbor(best_solution, neighborhood, improvement_strategy, rho)

        if current_solution is None:
            break
        else:
            best_solution = current_solution
            print(f"objective value of better solution: {objective_function(best_solution, rho)}")

    print(best_solution)

    return best_solution



def compute_neighborhood(customers, solution, neighborhood_structure, to_fulfilled):
    if neighborhood_structure == "exchange":
        neighborhood = compute_exchange_neighborhood(customers, solution)
    elif neighborhood_structure == "move":
        neighborhood = compute_move_neighborhood(customers, solution, to_fulfilled)
    elif neighborhood_structure == "2-move":
        neighborhood = compute_2_move_neighborhood(customers, solution, to_fulfilled)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")

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

def compute_2_move_neighborhood(customers, solution, to_fulfilled):
    neighborhood = []

    first_neighborhood = compute_move_neighborhood(customers, solution, to_fulfilled)
    for neighbor_i in first_neighborhood:
        neighborhood.append(neighbor_i)
        second_neighborhood = compute_move_neighborhood(customers, neighbor_i, to_fulfilled)
        for neighbor_j in second_neighborhood:
            if neighbor_j is not solution:
                neighborhood.append(neighbor_j)

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