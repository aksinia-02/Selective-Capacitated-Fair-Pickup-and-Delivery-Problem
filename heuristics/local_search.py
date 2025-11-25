from classes.Statistic import Statistic
from tools import *
from heuristics import construction
import copy
from heuristics.neighborhood_structures.neighborhood_core import choose_neighbor


def solve(customers, initial_solution, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best", output_statistic=False):
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

    statistic = Statistic(best_solution, rho)

    # If the solution is empty, it will be completed first
    if not is_solution_valid(best_solution, to_fulfilled):
        best_solution = construction.solve(customers, best_solution, to_fulfilled, rho, strategy="with_reordering")

    while True:
        current_solution = choose_neighbor(best_solution, customers, neighborhood_structure, improvement_strategy, to_fulfilled, rho)

        if current_solution is None:
            statistic.update(best_solution, rho)
            break
        else:
            best_solution = current_solution
            statistic.update(current_solution, rho)

    if output_statistic:
        return best_solution, statistic
    else:
        return best_solution



