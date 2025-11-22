from classes.ObjectiveTracker import ObjectiveTracker
from heuristics.neighborhood_structures.dropoff_relocate_neighborhood import compute_dropoff_relocate_neighbor
from heuristics.neighborhood_structures.exchange_neighborhood import compute_exchange_neighbor
from heuristics.neighborhood_structures.pickup_relocate_neighborhood import compute_pickup_relocate_neighbor


def choose_neighbor(solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho):
    tracker = ObjectiveTracker(solution, rho)
    if improvement_strategy != "first" and improvement_strategy != "best":
        raise ValueError(f"Unknown improvement strategy: {improvement_strategy}")
    if neighborhood_structure == "exchange":
        neighbor = compute_exchange_neighbor(solution, customers, improvement_strategy, tracker)
    elif neighborhood_structure == "pickup_relocate":
        neighbor = compute_pickup_relocate_neighbor(solution, customers, improvement_strategy, tracker)
    elif neighborhood_structure == "dropoff_relocate":
        neighbor = compute_dropoff_relocate_neighbor(solution, customers, improvement_strategy, tracker)
    else:
        raise ValueError(f"Unknown neighborhood structure: {neighborhood_structure}")
    return neighbor

# TODO: add neighborhood structures. Ideas:
# - swap two pickup points inside a vehicle
# - swap two dropoff points inside a vehicle
# - move one (pickup,dropoff)-pair inside a vehicle
# - swap two (pickup,dropoff)-pairs inside a vehicle (a part of exchange)
# - replace a (pickup,dropoff)-pair by a unfulfilled customer request (a part of exchange)
# - swap a (pickup,dropoff)-pair with another one of another vehicle (a part of exchange)
# - move a (pickup,dropoff)-pair to another vehicle (largest neighborhood)