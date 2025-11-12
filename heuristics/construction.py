from typing import List, Dict
import math
import itertools
import numpy as np

from classes.Point import Point
from classes.Customer import Customer
from classes.Vehicle import Vehicle

from tools import objective_function
import copy

def precompute_distance_matrix(customers: List[Customer], depot: Point):
    """Precompute all pairwise distances between customers and depot."""
    n = len(customers)
    coords = np.array([[c.pickup.x, c.pickup.y] for c in customers])
    depot_coord = np.array([depot.x, depot.y])

    dist_matrix = np.ceil(np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2)))
    depot_dist = np.ceil(np.sqrt(((coords - depot_coord) ** 2).sum(axis=1)))
    
    return dist_matrix, depot_dist

def calculate_savings_vectorized(dist_matrix, depot_dist):
    """Vectorized Clarke-Wright savings: S_ij = d(depot,i) + d(depot,j) - d(i,j)."""
    n = len(depot_dist)
    i_index, j_index = np.triu_indices(n, 1) # values above the diagonal (unordered pairs (i, j) with 0 <= i < j < n)
    savings_values = depot_dist[i_index] + depot_dist[j_index] - dist_matrix[i_index, j_index]
    savings = list(zip(zip(i_index + 1, j_index + 1), savings_values))
    return sorted(savings, key=lambda x: x[1], reverse=True)

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

def merge_with_reordering(vehicle_1, vehicle_2, n):

    merged_vehicle_1 = vehicle_1.copy()

    merged_path = vehicle_1.path[1:-1] + vehicle_2.path[1:-1]

    depot = vehicle_1.path[0]
    merged_vehicle_1.path = [depot]

    unselected_locations = [p for p in merged_path if p.type == 2]
    dropoffs = [p for p in merged_path if p.type == 3]

    while unselected_locations:
        feasible = [loc for loc in unselected_locations if merged_vehicle_1.load + loc.goods <= merged_vehicle_1.capacity]
        if not feasible:
            unselected_locations.extend([d for d in dropoffs if d.index == n + merged_vehicle_1.position.index])
        else:
            nearest_location = min(feasible, key=lambda loc: merged_vehicle_1.position.calculate_distance(loc))
            merged_vehicle_1.add_section_path(nearest_location)
            unselected_locations.remove(nearest_location)
            unselected_locations.extend([d for d in dropoffs if d.index == n + nearest_location.index])
    merged_vehicle_1.add_section_path(depot)

    return merged_vehicle_1

def merge_without_reordering(vehicle_1, vehicle_2, n):

    merged_vehicle = vehicle_1.copy()
    merged_vehicle.path = merged_vehicle.path[:-1] 

    depot = vehicle_1.path[0]

    for p in vehicle_2.path[1:]:
        if p.type == 2:
            if merged_vehicle.load + p.goods <= merged_vehicle.capacity:
                merged_vehicle.add_section_path(p)
        elif p.type == 3:
                merged_vehicle.add_section_path(p)

    merged_vehicle.add_section_path(depot)

    return merged_vehicle

def eliminate_sorted_pairs(sorted_pairs, merged_vehicle):

    type2_indices = {v.index for v in merged_vehicle.path if v.type == 2}
    return [
        pair for pair in sorted_pairs
        if not (pair[0][0] in type2_indices and pair[0][1] in type2_indices)
    ]

def solve(customers, vehicles, to_fullfilled, rho, strategy="pure"):

    depot = vehicles[0].path[0]
    num_customers = len(customers)

    dist_matrix, depot_dist = precompute_distance_matrix(customers, depot)
    sorted_pairs = calculate_savings_vectorized(dist_matrix, depot_dist)

    temp_vehicles = [Vehicle(i, vehicles[0].capacity, depot) for i in range(num_customers)]
    customer_to_vehicle: Dict[int, int] = {}

    for vehicle in vehicles:
        if len(vehicle.path) != 1:
            index = vehicle.index
            temp_vehicles[index].path = vehicle.path
            temp_vehicles[index].position = vehicle.position
            temp_vehicles[index].load = vehicle.load
            temp_vehicles[index].path_length = vehicle.path_length
            temp_vehicles[index].load_history = vehicle.load_history
            sorted_pairs = eliminate_sorted_pairs(sorted_pairs, temp_vehicles[index])
            for p in temp_vehicles[index].path:
                if p.type == 2:
                    customer_to_vehicle[p.index] = index

    for i in range(num_customers):
        if len(temp_vehicles[i].path) == 1:
            temp_vehicles[i].add_section_path(customers[i].pickup)
            temp_vehicles[i].add_section_path(customers[i].dropoff)
            temp_vehicles[i].add_section_path(depot)
            customer_to_vehicle[i + 1] = i

    switcher = {
        "with_reordering": merge_with_reordering,
        "pure": merge_without_reordering
    }

    cutoff = int(num_customers * 3)

    while True:

        best_objective_local = float('inf')
        best_merged_vehicle = None
        merge_i = remove_j = None
        
        for (i, j), saving in sorted_pairs[:cutoff]:

            vehicle_index_i = customer_to_vehicle.get(i)
            vehicle_index_j = customer_to_vehicle.get(j)
            if vehicle_index_i is None or vehicle_index_j is None or vehicle_index_i == vehicle_index_j:
                continue

            merged_vehicle = result = switcher.get(strategy, lambda: "unknown")(temp_vehicles[vehicle_index_i], temp_vehicles[vehicle_index_j], num_customers)
            #merged_vehicle = merge_without_reordering(temp_vehicles[vehicle_index_i], temp_vehicles[vehicle_index_j], num_customers)
        
            temp_copy = temp_vehicles.copy()
            temp_copy[vehicle_index_i] = merged_vehicle
            temp_copy.pop(vehicle_index_j)

            new_objective = objective_function(temp_copy, rho)

            if new_objective < best_objective_local:
                best_objective_local = new_objective
                best_merged_vehicle = merged_vehicle              
                merge_i, remove_j = vehicle_index_i, vehicle_index_j

        temp_vehicles[merge_i] = best_merged_vehicle
        temp_vehicles[remove_j].path = []
        for p in best_merged_vehicle.path:
            if p.type == 2:
                customer_to_vehicle[p.index] = best_merged_vehicle.index
        sorted_pairs = eliminate_sorted_pairs(sorted_pairs, best_merged_vehicle)

        max_temp_vehicles = selected = sorted(
            temp_vehicles,
            key=lambda v: (-len(v.path), sum(a.calculate_distance(b) for a, b in zip(v.path, v.path[1:])))
        )[:len(vehicles)]

        fullfilled_total = sum((len(v.path) - 2) / 2 for v in selected)
        print(f"Fullfilled: {fullfilled_total}")

        if fullfilled_total >= to_fullfilled:
            print(f"Not fullfilled customers: {num_customers - fullfilled_total}")
            return max_temp_vehicles