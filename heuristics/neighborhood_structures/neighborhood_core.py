from classes.ObjectiveTracker import ObjectiveTracker
from heuristics.neighborhood_structures.dropoff_relocate_neighborhood import compute_dropoff_relocate_neighbor
from heuristics.neighborhood_structures.exchange_neighborhood import compute_exchange_neighbor
from heuristics.neighborhood_structures.pickup_relocate_neighborhood import compute_pickup_relocate_neighbor
from heuristics.neighborhood_structures.remove_and_append_neighborhood import compute_remove_and_append_neighbor


def choose_neighbor(solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho):
    """
    This function returns a neighbor of solution depending on the choice of neighborhood_structure and improvement_strategy.

    solution: the solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    neighborhood_structure: the structure of the neighborhood. Valid values are "exchange", "pickup_relocate",
        "dropoff_relocate" and "remove_and_append".
    improvement_strategy: the improvement strategy. Valid values are: "best" and "first".
    to_fulfilled: the number of requests that need to be fulfilled.
    rho: the fairness weight.
    """

    tracker = ObjectiveTracker(solution, rho)
    if improvement_strategy != "first" and improvement_strategy != "best":
        raise ValueError(f"Unknown improvement strategy: {improvement_strategy}")
    if neighborhood_structure == "exchange":
        neighbor = compute_exchange_neighbor(solution, customers, improvement_strategy, tracker)
    elif neighborhood_structure == "pickup_relocate":
        neighbor = compute_pickup_relocate_neighbor(solution, customers, improvement_strategy, tracker)
    elif neighborhood_structure == "dropoff_relocate":
        neighbor = compute_dropoff_relocate_neighbor(solution, customers, improvement_strategy, tracker)
    elif neighborhood_structure == "remove_and_append":
        neighbor = compute_remove_and_append_neighbor(solution, customers, improvement_strategy, tracker)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")
    return neighbor

# more ideas for neighborhood structures:
# - remove and append + relocate pickup point
# - swap two pickup points inside a vehicle
# - swap two dropoff points inside a vehicle
# - move one (pickup,dropoff)-pair inside a vehicle
# - swap two (pickup,dropoff)-pairs inside a vehicle (a part of exchange)
# - replace a (pickup,dropoff)-pair by a unfulfilled customer request (a part of exchange)
# - swap a (pickup,dropoff)-pair with another one of another vehicle (a part of exchange)
# - move a (pickup,dropoff)-pair to another vehicle (largest neighborhood)