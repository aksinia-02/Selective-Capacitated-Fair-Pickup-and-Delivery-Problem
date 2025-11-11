import copy
from heuristics.local_search import solve as local_search
from heuristics.randomized_construction import solve as randomized_construction
from tools import objective_function


def solve(customers, vehicles, to_fulfilled, rho):
    best_solution = None
    no_improvement = 0
    max_no_improvement = 5

    while no_improvement < max_no_improvement:
        temp_solution = copy.deepcopy(vehicles)
        temp_solution = randomized_construction(customers, temp_solution, to_fulfilled, rho)
        current_solution = local_search(customers, temp_solution, to_fulfilled, rho) # can be changed to VND later

        if best_solution is None or objective_function(best_solution, rho) > objective_function(current_solution, rho):
            best_solution = current_solution
            no_improvement = 0
        else:
            no_improvement += 1
    return best_solution