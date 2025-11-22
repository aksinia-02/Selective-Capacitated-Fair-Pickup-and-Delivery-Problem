from tools import *
import copy
from heuristics.neighborhood_structures.neighborhood_utils import *

def compute_pickup_relocate_neighbor(solution, customers, improvement_strategy, tracker):
    stack = []

    for customer in customers:

        vehicle = find_vehicle(solution, customer.pickup)
        if vehicle is None:
            continue

        pickup_index = next(i for i, p in enumerate(vehicle.path) if p == customer.pickup)
        dropoff_index = next(i for i, p in enumerate(vehicle.path) if p == customer.dropoff)

        if dropoff_index >= 4:
            for i in range(1, dropoff_index):
                if i < pickup_index - 1 or i > pickup_index:
                    pred = vehicle.path[i]
                else:
                    continue

                path_length = predict_new_path_length_after_intra_point_relocate(vehicle, customer.pickup, pred)

                current_objective = tracker.predict_objective([vehicle.path_length], [path_length])
                if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                    if improvement_strategy == "first":
                        neighbor = copy.deepcopy(solution)
                        v = neighbor[vehicle.index]
                        relocate_point_in_vehicle(v, customer.pickup, pred)
                        if is_valid(v):
                            tracker.update(vehicle.path_length, v.path_length)
                            return neighbor
                    else:
                        stack.append([vehicle, customer, pred, current_objective])

    if improvement_strategy == "best" and stack:
        while stack:
            neighbor = copy.deepcopy(solution)
            vehicle, customer, pred, o = stack.pop()
            v = neighbor[vehicle.index]
            relocate_point_in_vehicle(v, customer.pickup, pred)
            if is_valid(v):
                tracker.update(vehicle.path_length, v.path_length)
                return neighbor
    return None