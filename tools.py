import math
from classes.Vehicle import Vehicle

def objective_function(vehicles, rho):
    total = sum(v.path_length for v in vehicles)
    squares = sum(v.path_length ** 2 for v in vehicles)
    jain_fairness = (total ** 2) / (len(vehicles) * squares)

    objective = total + rho * (1 - jain_fairness)

    return objective

def find_vehicle(solution, node):
    for v in solution:
        if node in v.path:
            return v
    return None

def is_valid(vehicle):
    for load in vehicle.load_history:
        if load > vehicle.capacity:
            return False
    return True

def is_solution_valid(solution, to_fulfilled):
    fulfilled = 0
    for vehicle in solution:
        if not is_valid(vehicle):
            return False
        fulfilled = fulfilled + len(vehicle.path)/2
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