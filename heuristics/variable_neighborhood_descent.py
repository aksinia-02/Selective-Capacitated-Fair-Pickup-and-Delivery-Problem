import copy
from heuristics.neighborhood_structures.neighborhood_core import choose_neighbor
from tools import *
from heuristics import construction

def solve(customers, initial_solution, to_fulfilled, rho, neighborhood_structures=None, improvement_strategy="best"):
    """
    This function solves the heuristic problem using variable neighborhood descent.

    customers: is a list of customer objects, each customer object contains information about a customer request.
    initial_solution: the initial solution of the heuristic problem. (a list of vehicle objects)
    to_fulfilled: the number of requests that need to be fulfilled.
    rho: the fairness weight.
    neighborhood_structures: a list of neighborhood structures. Valid values are "exchange", "pickup_relocate",
        "dropoff_relocate" and "remove_and_append". If None, it will be initialized with
        ["pickup_relocate", "dropoff_relocate", "exchange"]
    improvement_strategy: the improvement strategy. Valid values are: "best" and "first".
    """

    if neighborhood_structures is None:
        neighborhood_structures = ["pickup_relocate", "dropoff_relocate", "exchange"]

    best_solution = copy.deepcopy(initial_solution)

    # If the solution is empty, it will be completed first
    if not is_solution_valid(best_solution, to_fulfilled):
        best_solution = construction.solve(customers, best_solution, to_fulfilled, rho, strategy="with_reordering")

    l = 0 # index of neighborhood structure
    l_max = len(neighborhood_structures)

    while l < l_max:
        print(l)
        current_solution = choose_neighbor(best_solution, customers, neighborhood_structures[l], improvement_strategy, to_fulfilled, rho)

        if current_solution is None:
            l = l + 1
        else:
            best_solution = current_solution
            l = 0
    return best_solution