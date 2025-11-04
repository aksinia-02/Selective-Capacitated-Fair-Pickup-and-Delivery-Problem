from tools import objective_function
from heuristics import randomized_construction


def solve(customers, vehicles, to_fullfilled, rho):
    randomized_construction.solve(customers, vehicles, to_fullfilled, rho) # initial solution in vehicles
    for i in range(0, 2000): # TODO: change stopping criterion
        neighborhood = compute_neighborhood(vehicles)
        current_solution = select_neighbor(neighborhood)

        if objective_function(current_solution, rho) <= objective_function(vehicles, rho):
            vehicles = current_solution


def compute_neighborhood(solution):
    neighborhood = []
    # TODO: add 3 different kind of neighbourhoods

    return neighborhood

def select_neighbor(neighbors):
    neighbor = neighbors[0]
    # TODO: add best-improvement and first-improvement

    return neighbor