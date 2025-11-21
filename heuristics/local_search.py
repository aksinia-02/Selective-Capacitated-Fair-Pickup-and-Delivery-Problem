from tools import *
from heuristics import construction
import copy
from heuristics.neighborhood_structures.neighborhood_core import choose_neighbor


def solve(customers, initial_solution, to_fulfilled, rho, neighborhood_structure="exchange", improvement_strategy="best"):
    best_solution = copy.deepcopy(initial_solution)
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

    print(best_solution)

    return best_solution



