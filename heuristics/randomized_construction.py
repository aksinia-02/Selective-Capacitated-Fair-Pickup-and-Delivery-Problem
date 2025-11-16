from typing import List, Dict, Iterator, Tuple
import heapq
import random

from classes.Point import Point
from classes.Customer import Customer
from classes.Vehicle import Vehicle

from tools import objective_function
import copy

def savings_generator(customers, depot, customer_to_vehicle, cutoff=None):
    """
    heapq saves (i,j) and saving values on the fly without precomputing matrices
    """
    heap = []
    n = len(customers)
    
    for i in range(n):
        for j in range(i+1, n):
            vi = customer_to_vehicle.get(i+1)
            vj = customer_to_vehicle.get(j+1)
            if vi is None or vj is None or vi == vj:
                continue
            s = (depot.calculate_distance(customers[i].pickup) + depot.calculate_distance(customers[j].pickup) - customers[i].pickup.calculate_distance(customers[j].pickup))
            
            if cutoff:
                heapq.heappush(heap, (s, i+1, j+1))
                if len(heap) > cutoff:
                    heapq.heappop(heap)
            else:
                yield (i+1, j+1), s
    
    if cutoff:
        # return in descending order
        for s, i, j in sorted(heap, key=lambda x: -x[0]):
            yield (i, j), s


def merge_with_reordering(vehicle_1, vehicle_2, n):

    merged_vehicle_1 = vehicle_1.copy()
    merged_vehicle_1.path_length = 0

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

def solve(customers, vehicles, to_fullfilled, rho, strategy="pure"):

    depot = vehicles[0].path[0]
    num_customers = len(customers)

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
            if temp_vehicles[index].path[-1] != depot:
                temp_vehicles[index].add_section_path(depot)
                
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

        improving_merges = []

        best_objective_local = float('inf')
        best_merged_vehicle = None
        merge_i = remove_j = None

        savings_iter = savings_generator(customers, depot, customer_to_vehicle, cutoff=cutoff)
        
        for (i, j), saving in savings_iter:

            vehicle_index_i = customer_to_vehicle.get(i)
            vehicle_index_j = customer_to_vehicle.get(j)

            merged_vehicle = switcher.get(strategy, lambda: "unknown")(temp_vehicles[vehicle_index_i], temp_vehicles[vehicle_index_j], num_customers)
        
            temp_copy = temp_vehicles.copy()
            temp_copy[vehicle_index_i] = merged_vehicle
            temp_copy.pop(vehicle_index_j)

            new_objective = objective_function(temp_copy, rho)

            if new_objective < best_objective_local:
                improving_merges.append((vehicle_index_i, vehicle_index_j, merged_vehicle))

        merge_i, remove_j, best_merged_vehicle = random.choice(improving_merges)

        temp_vehicles[merge_i] = best_merged_vehicle
        temp_vehicles[remove_j].path = []
        for p in best_merged_vehicle.path:
            if p.type == 2:
                customer_to_vehicle[p.index] = best_merged_vehicle.index

        max_temp_vehicles = selected = sorted(
            temp_vehicles,
            key=lambda v: (-len(v.path), sum(a.calculate_distance(b) for a, b in zip(v.path, v.path[1:])))
        )[:len(vehicles)]

        fullfilled_total = sum((len(v.path) - 2) / 2 for v in selected)
        print(f"Fullfilled: {fullfilled_total}")

        if fullfilled_total >= to_fullfilled:
            print(f"Not fullfilled customers: {num_customers - fullfilled_total}")
            for i, v in enumerate(max_temp_vehicles):
                v.index = i
            return max_temp_vehicles