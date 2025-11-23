from tools import *
import copy
from heuristics.neighborhood_structures.neighborhood_utils import *

def compute_dropoff_relocate_neighbor(solution, customers, improvement_strategy, tracker):
    """
    This function returns a neighbor of the dropoff_relocate neighborhood depending on the improvement_strategy.
    (one dropoff point is relocated inside a vehicle)

    solution: the solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    improvement_strategy: the improvement strategy. Valid values are: "best" and "first".
    tracker: this object is used to efficiently track the quality of different neighbors.
    """

    stack = []

    for customer in customers:

        vehicle = find_vehicle(solution, customer.dropoff)
        if vehicle is None:
            continue

        pickup_index = next(i for i, p in enumerate(vehicle.path) if p == customer.pickup)
        dropoff_index = next(i for i, p in enumerate(vehicle.path) if p == customer.dropoff)

        for i in range(pickup_index, len(vehicle.path) - 1):
            if i < dropoff_index - 1 or i > dropoff_index:
                pred = vehicle.path[i]
            else:
                continue

            path_length = predict_new_path_length_after_intra_point_relocate(vehicle, customer.dropoff, pred)

            current_objective = tracker.predict_objective([vehicle.path_length], [path_length])
            if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                if improvement_strategy == "first":
                    neighbor = copy.deepcopy(solution)
                    v = neighbor[vehicle.index]
                    relocate_point_in_vehicle(v, customer.dropoff, pred)
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
            relocate_point_in_vehicle(v, customer.dropoff, pred)
            if is_valid(v):
                tracker.update(vehicle.path_length, v.path_length)
                return neighbor
    return None