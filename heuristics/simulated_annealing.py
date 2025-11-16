from tools import *
from heuristics import construction
from typing import Dict
import random
from classes.Vehicle import Vehicle

from classes.ObjectiveTracker import ObjectiveTracker

def group_customers_by_vehicle(customer_to_vehicle):
    vehicle_to_customers = {}

    for customer, vehicle in customer_to_vehicle.items():
        if vehicle not in vehicle_to_customers:
            vehicle_to_customers[vehicle] = []
        vehicle_to_customers[vehicle].append(customer)

    return vehicle_to_customers

def reorder_path(vehicle, path, n):

    depot = vehicle.path[0]

    unselected_locations = [p for p in path if p.type == 2]
    dropoffs = [p for p in path if p.type == 3]

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
    return vehicle

def swap_two_customers(x, c1, c2, veh1, veh2, n):

    result_vehicles = x.copy()

    print(f"Swap {c1} with {c2} wiht vehicles {veh1} and {veh2}")

    vehicle_1 = x[veh1].copy() if veh1 < len(x) else None
    vehicle_2 = x[veh2].copy() if veh2 < len(x) else None

    pickup_c1 = None if vehicle_1 is None else next(p for p in vehicle_1.path if p.index == c1)
    dropoff_c1 = None if vehicle_1 is None else next(p for p in vehicle_1.path if p.index == (c1 + n))
    pickup_c2 = None if vehicle_2 is None else next(p for p in vehicle_2.path if p.index == c2)
    dropoff_c2 = None if vehicle_2 is None else next(p for p in vehicle_2.path if p.index == (c2 + n))

    print(f"Swap {pickup_c1}, {dropoff_c1} wiht {pickup_c2}, {dropoff_c2}")

    if vehicle_1 is not None:
        new_path = []

        for point in vehicle_1.path[1:-1]:
            if point != pickup_c1 and point != dropoff_c1:
                new_path.append(point)

        print(vehicle_1.path_length)
        new_vehicle_1 = Vehicle(vehicle_1.index, vehicle_1.capacity, vehicle_1.position)
        new_vehicle_1 = reorder_path(new_vehicle_1, new_path, n)
        print(new_vehicle_1.path_length)

    if vehicle_2 is not None:
        new_path = []

        for point in vehicle_2.path[1:-1]:
            if point != pickup_c1 and point != dropoff_c1:
                new_path.append(point)

        print(vehicle_1.path_length)
        new_vehicle_2= Vehicle(vehicle_2.index, vehicle_2.capacity, vehicle_2.position)
        new_vehicle_2 = reorder_path(new_vehicle_2, new_path, n)
        print(new_vehicle_2.path_length)

    result_vehicles[veh1] = new_vehicle_1
    result_vehicles[veh2] = new_vehicle_2
    return result_vehicles



def random_choose_swap_two_customers(x, customer_to_vehicle, n):

    vehicle_to_customers = group_customers_by_vehicle(customer_to_vehicle)
    not_fullfilled = set(range(1, n + 1)) - set(customer_to_vehicle.keys())
    vehicle_list = list(vehicle_to_customers.items()) + [(len(x), list(not_fullfilled))]

    (veh1, custs1), (veh2, custs2) = random.sample(vehicle_list, 2)

    c1 = random.choice(custs1)
    c2 = random.choice(custs2)

    return swap_two_customers(x, c1, c2, veh1, veh2, n)

    

def solve(customers, vehicles, to_fulfilled, rho):

    global objectiveTracker
    x = construction.solve(customers, vehicles, to_fulfilled, rho)

    customer_to_vehicle: Dict[int, int] = {}

    for i, vehicle in enumerate(x):
            for p in vehicle.path:
                if p.type == 2:
                    customer_to_vehicle[p.index] = i

    objectiveTracker = ObjectiveTracker(x, rho)

    neighborhood_size =  len(customers) * (len(customers) - 1) / 2
    equilibrium_cond = 4 * neighborhood_size
    x_new = random_choose_swap_two_customers(x, customer_to_vehicle, len(customers))