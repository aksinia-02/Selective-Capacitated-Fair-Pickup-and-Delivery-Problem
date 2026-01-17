import math
from classes.Vehicle import Vehicle

def objective_function(vehicles, rho, name="jain"):
    """
    This function computes and returns the objective value of a solution.
    """

    total = sum(v.path_length for v in vehicles)

    if name == "jain":
        squares = sum(v.path_length ** 2 for v in vehicles)
        fairness = (total ** 2) / (len(vehicles) * squares)
    elif name == "min_max":
        fairness = max_min_fairness(vehicles)
    else:
        fairness = gini_coefficient(vehicles)

    objective = total + rho * (1 - fairness)

    return objective



def max_min_fairness(vehicles):

    lengths = [v.path_length for v in vehicles]

    min_length = min(lengths)
    max_length = max(lengths)

    if max_length == 0:
        return 0
    
    return max(min_length / max_length, 1e-6)

def gini_coefficient(vehicles):

    lengths = [v.path_length for v in vehicles]
    n = len(lengths)

    total_length = sum(lengths)

    if total_length == 0:
        return 1
    
    diff_sum = 0
    for i in range(n):
        for j in range(n):
            diff_sum += abs(lengths[i] - lengths[j])

    return 1 - diff_sum / (2 * n * total_length)

def objective_function_detailed(vehicles, rho):
    """
    This function computes and returns the objective value of a solution.
    """

    total = sum(v.path_length for v in vehicles)
    squares = sum(v.path_length ** 2 for v in vehicles)
    jain_fairness = (total ** 2) / (len(vehicles) * squares)

    objective = total + rho * (1 - jain_fairness)

    return objective, total, jain_fairness


def find_vehicle(solution, node):
    """
    returns the vehicle containing node in its path if it exists.
    """

    for v in solution:
        if node in v.path:
            return v
    return None


def is_valid(vehicle, customers=None):
    """
    checks whether a vehicle is valid.
    """
    if customers is not None:
        for c in customers:
            if c.pickup in vehicle.path and c.dropoff in vehicle.path:
                if vehicle.path.index(c.pickup) > vehicle.path.index(c.dropoff):
                    return False

    for load in vehicle.load_history:
        if load > vehicle.capacity:
            return False
    return True

def is_solution_valid(solution, to_fulfilled):
    """
    checks whether a solution is valid.
    """

    fulfilled = 0
    for vehicle in solution:
        if not is_valid(vehicle):
            return False
        fulfilled = fulfilled + len(vehicle.path)/2 - 1
    return fulfilled >= to_fulfilled

def reorder_paths(vehicles, n):

    for i, v in enumerate(vehicles):

        vehicle = Vehicle(v.index, v.capacity, v.position)

        depot = vehicle.path[0]

        unselected_locations = [p for p in v.path if p.type == 2]
        dropoffs = [p for p in v.path if p.type == 3]

        while unselected_locations:
            feasible = [loc for loc in unselected_locations if vehicle.load + loc.goods <= vehicle.capacity]
            if not feasible:
                unselected_locations.extend([d for d in dropoffs if d.index == n + vehicle.position.index])
            else:
                nearest_location = min(feasible, key=lambda loc: vehicle.position.calculate_distance(loc))
                vehicle.add_section_path(nearest_location)
                unselected_locations.remove(nearest_location)
                unselected_locations.extend([d for d in dropoffs if d.index == n + nearest_location.index])
        vehicle.add_section_path(depot)
        vehicles[i] = vehicle
    return vehicles