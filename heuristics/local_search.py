from tools import *
from heuristics import construction
import copy
from heuristics.neighborhood_structures.neighborhood_core import choose_neighbor


def solve(customers, initial_solution, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best"):
    """
    This function solves the heuristic problem using local search.

    customers: is a list of customer objects, each customer object contains information about a customer request.
    initial_solution: the initial solution of the heuristic problem. (a list of vehicle objects)
    to_fulfilled: the number of requests that need to be fulfilled.
    rho: the fairness weight.
    neighborhood_structure: the structure of the neighborhood. Valid values are "exchange", "pickup_relocate",
        "dropoff_relocate", "remove_and_append" and "move".
    improvement_strategy: the improvement strategy. Valid values are: "best" and "first".
    """

    best_solution = copy.deepcopy(initial_solution)

    # If the solution is empty, it will be completed first
    if not is_solution_valid(best_solution, to_fulfilled):
        best_solution = construction.solve(customers, best_solution, to_fulfilled, rho, strategy="with_reordering")

    print(f"objective value of first solution: {objective_function(best_solution, rho)}")

    while True:
        current_solution = choose_neighbor(best_solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho)
        if current_solution is None:
            break
        else:
            best_solution = current_solution
            print(f"objective value of better solution: {objective_function(best_solution, rho)}")

    return best_solution



