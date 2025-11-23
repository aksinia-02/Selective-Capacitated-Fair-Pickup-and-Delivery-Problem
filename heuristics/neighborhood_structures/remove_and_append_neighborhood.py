from tools import *
import copy
from heuristics.neighborhood_structures.neighborhood_utils import *

def compute_remove_and_append_neighbor(solution, customers, improvement_strategy, tracker):
    """
    This function returns a neighbor of the remove_and_append neighborhood depending on the improvement_strategy.
    (one pickup and dropoff point removed from a vehicle and appended to another vehicle)

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

            vehicle_path_length, destination_vehicle_path_length = predict_new_path_lengths_after_remove_and_append(vehicle, destination_vehicle, customer)

            current_objective = tracker.predict_objective([vehicle.path_length, destination_vehicle.path_length], [vehicle_path_length, destination_vehicle_path_length])
            if current_objective < tracker.objective_value and (not stack or current_objective < stack[-1][-1]):
                if improvement_strategy == "first":
                    neighbor = copy.deepcopy(solution)
                    v = neighbor[vehicle.index]
                    dv = neighbor[destination_vehicle.index]
                    perform_remove_and_append(v, dv, customer)
                    if is_valid(v) and is_valid(dv):
                        tracker.update(vehicle.path_length, v.path_length)
                        tracker.update(destination_vehicle.path_length, dv.path_length)
                        return neighbor
                else:
                    stack.append([vehicle, destination_vehicle, customer, current_objective])

    if improvement_strategy == "best" and stack:
        while stack:
            neighbor = copy.deepcopy(solution)
            vehicle, destination_vehicle, customer, o = stack.pop()
            v = neighbor[vehicle.index]
            dv = neighbor[destination_vehicle.index]
            perform_remove_and_append(v, dv, customer)
            if is_valid(v) and is_valid(dv):
                tracker.update(vehicle.path_length, v.path_length)
                tracker.update(destination_vehicle.path_length, dv.path_length)
                return neighbor
    return None


def perform_remove_and_append(vehicle, destination_vehicle, customer):
    """
    This function performs the remove and append action.

    vehicle: the vehicle object from which a request is removed.
    destination_vehicle: the vehicle object to which a request is appended.
    customer: customer object containing information about a customer request.
    """

    vehicle.remove_section_path(customer.pickup)
    vehicle.remove_section_path(customer.dropoff)
    destination_vehicle.add_section_path_after(destination_vehicle.path[-2], customer.pickup)
    destination_vehicle.add_section_path_after(destination_vehicle.path[-2], customer.dropoff)