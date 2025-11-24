from classes.ObjectiveTracker import ObjectiveTracker
from heuristics.neighborhood_structures.dropoff_relocate_neighborhood import compute_dropoff_relocate_neighbor
from heuristics.neighborhood_structures.exchange_neighborhood import compute_exchange_neighbor
from heuristics.neighborhood_structures.move_neighborhood import compute_move_neighbor
from heuristics.neighborhood_structures.pickup_relocate_neighborhood import compute_pickup_relocate_neighbor
from heuristics.neighborhood_structures.remove_and_append_neighborhood import compute_remove_and_append_neighbor


def choose_neighbor(solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho):
    """
    This function returns a neighbor of solution depending on the choice of neighborhood_structure and improvement_strategy.

    solution: the solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    neighborhood_structure: the structure of the neighborhood. Valid values are "exchange", "pickup_relocate",
        "dropoff_relocate", "remove_and_append" and "move".
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
    elif neighborhood_structure == "move":
        neighbor = compute_move_neighbor(solution, customers, improvement_strategy, tracker)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")
    return neighbor