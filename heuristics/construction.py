from typing import List
import math
import itertools

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
        savings[(i + 1, j + 1)] = s
    return sorted(savings.items(), key=lambda x: x[1], reverse=True)

def extract_unique_indices(sorted_pairs):
    seen = set()
    ordered_indices = []
    for (i, j), _ in sorted_pairs:
        if i not in seen:
            ordered_indices.append(i)
            seen.add(i)
        if j not in seen:
            ordered_indices.append(j)
            seen.add(j)
    return ordered_indices

def total_distance(sequence):
    distance = 0
    for i in range(len(sequence) - 1):
        distance += sequence[i].calculate_distance(sequence[i + 1])
    return distance

def merge(vehicle_1, vehicle_2, n):

    merged_path = vehicle_1.path[1:-1] + vehicle_2.path[1:-1]

    depot = vehicle_1.path[0]
    vehicle_1.path = [depot]

    unselected_locations = [p for p in merged_path if p.type == 2]
    dropoffs = [p for p in merged_path if p.type == 3]

    while len(unselected_locations) != 0:
        feasible = [loc for loc in unselected_locations if vehicle_1.load + loc.goods <= vehicle_1.capacity]
        if len(feasible) == 0:
            unselected_locations.extend([d for d in dropoffs if d.index == n + vehicle_1.position.index])
        else:
            nearest_location = min(feasible, key=lambda loc: vehicle_1.position.calculate_distance(loc))
            vehicle_1.add_section_path(nearest_location)
            unselected_locations.remove(nearest_location)
            unselected_locations.extend([d for d in dropoffs if d.index == n + nearest_location.index])
    vehicle_1.add_section_path(depot)

    return vehicle_1

def eliminate_sorted_pairs(sorted_pairs, merged_vehicle):

    type2_indices = {v.index for v in merged_vehicle.path if v.type == 2}
    return [
        pair for pair in sorted_pairs
        if not (pair[0][0] in type2_indices and pair[0][1] in type2_indices)
    ]

def solve(customers, vehicles, to_fullfilled, rho):

    depot = vehicles[0].position
    num_customers = len(customers)

    temp_vehicles = [Vehicle(i, vehicles[0].capacity, depot) for i in range(num_customers)]

    for i in range(num_customers):
        temp_vehicles[i].add_section_path(customers[i].pickup)
        temp_vehicles[i].add_section_path(customers[i].dropoff)
        temp_vehicles[i].add_section_path(depot)

    sorted_pairs = calculate_savings(customers, depot)

    while True:

        best_objective_local = float('inf')
        best_merged_vehicle, merged_index = None, None
        to_remove = None
        
        for (i, j), saving in sorted_pairs[:num_customers]:

            vehicle_index_i = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == i for p in v.path)), None)
            vehicle_index_j = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == j for p in v.path)), None)
            
            if vehicle_index_i is not None and vehicle_index_j is not None and vehicle_index_i != vehicle_index_j:

                candidate_vehicle_i = copy.deepcopy(temp_vehicles[vehicle_index_i])
                candidate_vehicle_j = copy.deepcopy(temp_vehicles[vehicle_index_j])

                merged_vehicle = merge(candidate_vehicle_i, candidate_vehicle_j, num_customers)
        
                temp_copy = temp_vehicles.copy()
                temp_copy[vehicle_index_i] = merged_vehicle
                temp_copy.pop(vehicle_index_j)

                new_objective = objective_function(temp_copy, rho)

                if new_objective < best_objective_local:
                    best_objective_local = new_objective
                    best_merged_vehicle = merged_vehicle
                    to_remove = vehicle_index_j
                    merged_index = vehicle_index_i

        temp_vehicles[merged_index] = best_merged_vehicle
        temp_vehicles.pop(to_remove)
        sorted_pairs = eliminate_sorted_pairs(sorted_pairs, best_merged_vehicle)

        num_to_select = len(vehicles)

        sorted_temp_vehicles = sorted(
            temp_vehicles,
            key=lambda v: (-len(v.path), total_distance(v.path))
        )
        max_temp_vehicles = sorted_temp_vehicles[:num_to_select]

        fullfilled_total = 0
        for v in max_temp_vehicles:
            fullfilled_total += (len(v.path) - 2)/2
        print(f"Fullfilled: {fullfilled_total}")

        if fullfilled_total >= to_fullfilled:
            print(f"Not fullfilled customers: {num_customers - fullfilled_total}")
            return max_temp_vehicles