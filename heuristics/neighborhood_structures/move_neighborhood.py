from tools import *
import copy
from heuristics.neighborhood_structures.neighborhood_utils import *

def compute_move_neighbor(solution, customers, improvement_strategy, tracker):
    """
    This function returns a neighbor of the move depending on the improvement_strategy.
    (one pickup and dropoff point removed from a vehicle and inserted somewhere into another vehicle)

    solution: the solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    improvement_strategy: the improvement strategy. Valid values are: "best" and "first".
    tracker: this object is used to efficiently track the quality of different neighbors.
    """

    stack = []

    for customer in customers:
        vehicle = find_vehicle(solution, customer.pickup)
        if vehicle is None:
            continue

        for destination_vehicle in solution:
            if vehicle == destination_vehicle:
                continue

            for i in range(1, len(destination_vehicle.path)):
                for j in range(i + 1, len(destination_vehicle.path)):
                    vehicle_path_length, destination_vehicle_path_length = predict_new_path_lengths_after_move(vehicle, destination_vehicle, customer, destination_vehicle.path[i], destination_vehicle.path[j])

                    current_objective = tracker.predict_objective([vehicle.path_length, destination_vehicle.path_length], [vehicle_path_length, destination_vehicle_path_length])
                    if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                        if improvement_strategy == "first":
                            neighbor = copy.deepcopy(solution)
                            v = neighbor[vehicle.index]
                            dv = neighbor[destination_vehicle.index]
                            perform_move(v, dv, customer, dv.path[i], dv.path[j])
                            if is_valid(v) and is_valid(dv):
                                tracker.update(vehicle.path_length, v.path_length)
                                tracker.update(destination_vehicle.path_length, dv.path_length)
                                return neighbor
                        else:
                            stack.append([vehicle, destination_vehicle, customer, i, j, current_objective])

    if improvement_strategy == "best" and stack:
        while stack:
            neighbor = copy.deepcopy(solution)
            vehicle, destination_vehicle, customer, i, j, o = stack.pop()
            v = neighbor[vehicle.index]
            dv = neighbor[destination_vehicle.index]
            perform_move(v, dv, customer, dv.path[i], dv.path[j])
            if is_valid(v) and is_valid(dv):
                tracker.update(vehicle.path_length, v.path_length)
                tracker.update(destination_vehicle.path_length, dv.path_length)
                return neighbor
    return None


def perform_move(vehicle, destination_vehicle, customer, pickup_pred, dropoff_pred):
    """
    This function performs the move action.

    vehicle: the vehicle object from which a request is removed.
    destination_vehicle: the vehicle object to which a request is appended.
    customer: customer object containing information about a customer request.
    pickup_pred: the new predecessor of the pickup point.
    dropoff_pred: the new predecessor of the dropoff point.
    """

    if vehicle is not None:
        vehicle.remove_section_path(customer.pickup)
        vehicle.remove_section_path(customer.dropoff)
    destination_vehicle.add_section_path_after(dropoff_pred, customer.dropoff)
    destination_vehicle.add_section_path_after(pickup_pred, customer.pickup)