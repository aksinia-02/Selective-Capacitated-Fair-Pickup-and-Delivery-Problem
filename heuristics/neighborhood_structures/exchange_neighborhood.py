from tools import *
import copy
from heuristics.neighborhood_structures.neighborhood_utils import *

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