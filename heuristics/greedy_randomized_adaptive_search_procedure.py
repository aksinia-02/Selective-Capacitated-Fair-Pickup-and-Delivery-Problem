import copy
from heuristics.variable_neighborhood_descent import solve as variable_neighborhood_descent
from heuristics.randomized_construction import solve as randomized_construction
from tools import objective_function


def solve(customers, vehicles, to_fulfilled, rho):
    """
    This function solves the heuristic problem using the greedy randomized adaptive search procedure.
    It uses VND with its default neighborhood structures and best improvement.

    customers: is a list of customer objects, each customer object contains information about a customer request.
    initial_solution: the initial solution of the heuristic problem. (a list of vehicle objects)
    to_fulfilled: the number of requests that need to be fulfilled.
    rho: the fairness weight.
    """

    best_solution = None
    no_improvement = 0
    max_no_improvement = 10

    while no_improvement < max_no_improvement:
        temp_solution = copy.deepcopy(vehicles)
        temp_solution = randomized_construction(customers, temp_solution, to_fulfilled, rho)
        current_solution = variable_neighborhood_descent(customers, temp_solution, to_fulfilled, rho)

        if best_solution is None or objective_function(best_solution, rho) > objective_function(current_solution, rho):
            best_solution = current_solution
            no_improvement = 0
        else:
            no_improvement += 1
    return best_solution