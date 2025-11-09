from typing import List
import math
import itertools
import random

from classes.Point import Point
from classes.Customer import Customer
from classes.Vehicle import Vehicle

from tools import objective_function
import copy

def calculate_savings(customers, depot):
    """
    Calculate the Clarke-Wright savings for all pairs of customers
    S_ij = d(depot,i) + d(j,depot) - d(i,j)
    """
    savings = {}
    for i, j in itertools.combinations(range(len(customers)), 2):
        s = (depot.calculate_distance(customers[i].pickup) + depot.calculate_distance(customers[j].pickup) - customers[i].pickup.calculate_distance(customers[j].pickup))
        savings[(i, j)] = s
    return sorted(savings.items(), key=lambda x: x[1], reverse=True)

def total_distance(sequence):
    distance = 0
    for i in range(len(sequence) - 1):
        distance += sequence[i].calculate_distance(sequence[i + 1])
    return distance

def merge(vehicle_1, vehicle_2, rho):

    merged_path = vehicle_1.path[1:-1] + vehicle_2.path[1:-1]

    depot = vehicle_1.path[0]
    vehicle_1.path = [depot]

    unselected_locations = [p for p in merged_path if p.type == 2]
    dropoffs = [p for p in merged_path if p.type == 3]

    while len(unselected_locations) != 0:
        feasible = [loc for loc in unselected_locations if vehicle_1.load + loc.goods <= vehicle_1.capacity]
        feasible_sorted = sorted(feasible, key=lambda loc: vehicle_1.position.calculate_distance(loc))
        top_k = max(1, int(rho * len(feasible_sorted)))

        # random_location = random.choice(feasible_sorted[:top_k])
        # vehicle_1.add_section_path(random_location, random_location.goods)
        # unselected_locations.remove(random_location)
        # unselected_locations.extend([d for d in dropoffs if d.index == 50 + random_location.index])
        nearest_location = min(feasible, key=lambda loc: vehicle_1.position.calculate_distance(loc))
        vehicle_1.add_section_path(nearest_location, nearest_location.goods)
        unselected_locations.remove(nearest_location)
        unselected_locations.extend([d for d in dropoffs if d.index == 50 + nearest_location.index])

    vehicle_1.add_section_path(depot)

    return vehicle_1


def solve(customers, vehicles, to_fullfilled, rho):

    depot = vehicles[0].position

    min_function = math.inf
    sorted_pairs = calculate_savings(customers, depot)

    temp_vehicles = [Vehicle(i, vehicles[0].capacity, depot) for i in range(len(customers))]

    for i in range(len(customers)):
        temp_vehicles[i].add_section_path(customers[i].pickup, customers[i].goods)
        temp_vehicles[i].add_section_path(customers[i].dropoff, -customers[i].goods)
        temp_vehicles[i].add_section_path(depot)

    best_objective = float('inf')

    remaining_pairs = copy.deepcopy(sorted_pairs)

    while len(sorted_pairs) != 0:
        top_k = max(1, int(rho * len(remaining_pairs)))
        (i,j), _ = random.choice(remaining_pairs[:top_k])
        remaining_pairs.remove(((i,j), _))

        vehicle_index_i = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == i for p in v.path)), None)
        vehicle_index_j = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == j for p in v.path)), None)
        
        if vehicle_index_i is not None and vehicle_index_j is not None and vehicle_index_i != vehicle_index_j:

            candidate_vehicle_i = copy.deepcopy(temp_vehicles[vehicle_index_i])
            candidate_vehicle_j = copy.deepcopy(temp_vehicles[vehicle_index_j])

            merged_vehicle = merge(candidate_vehicle_i, candidate_vehicle_j, rho)
    
            temp_copy = temp_vehicles.copy()
            temp_copy[vehicle_index_i] = merged_vehicle
            temp_copy.pop(vehicle_index_j)

            new_objective = objective_function(temp_copy, rho)
            print(f"new: {new_objective}")
    
            # Compute current objective
            print(f"current: {best_objective}")

            if new_objective * 0.75 < best_objective:
                temp_vehicles[vehicle_index_i] = merged_vehicle
                temp_vehicles.pop(vehicle_index_j)
                best_objective = new_objective
                print(f"set new objective: {best_objective}")

        num_to_select = len(vehicles)

        sorted_temp_vehicles = sorted(
            temp_vehicles,
            key=lambda v: (-len(v.path), total_distance(v.path))
        )
        max_temp_vehicles = sorted_temp_vehicles[:num_to_select]

        fullfilled_total = 0
        for v in max_temp_vehicles:
            fullfilled_total += (len(v.path) - 2)/2

        if fullfilled_total >= to_fullfilled:
            print(f"Not fullfilled customers: {len(customers) - fullfilled_total}")
            return max_temp_vehicles
    return None