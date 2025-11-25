from classes.Statistic import Statistic
from tools import *
from heuristics import construction
import copy


def solve(customers, vehicles, to_fulfilled, rho, output_statistic=False):
    """
    This function solves the heuristic problem using pilot search.

    customers: is a list of customer objects, each customer object contains information about a customer request.
    initial_solution: the initial solution of the heuristic problem. (a list of vehicle objects)
    to_fulfilled: the number of requests that need to be fulfilled.
    rho: the fairness weight.
    strategy: "light" or "intensive". The light variant is much faster, but the intensive strategy yields better results.
    """

    x = copy.deepcopy(vehicles)


    x_best = None
    statistic = Statistic()

    while not is_complete(x, to_fulfilled):

        C = satisfy_one_more_customer(x, customers)

        c_best = None
        best_x_temp = None
        best_val = float("inf")

        # Evaluate all candidates and pick the best one this iteration
        for c in C:

            # compute x_temp
            if x_best is None or not is_prefix(c, x_best):
                x_temp = construction.solve(customers, copy.deepcopy(c), to_fulfilled, rho)
            else:
                x_temp = x_best

            val = objective_function(x_temp, rho)

            # keep best candidate in this iteration
            if val < best_val:
                best_val = val
                best_x_temp = x_temp
                c_best = c

        # move to next partial solution
        x = c_best

        # update global best if improved
        if x_best is None or best_val < objective_function(x_best, rho):
            x_best = best_x_temp

        statistic.update(x_best, rho)

    if output_statistic:
        return x_best, statistic
    else:
        return x_best


def is_complete(solution, to_fulfilled):
    """
    This function returns whether enough customer requests are fulfilled in order to be a complete solution.

    solution: the current solution of the heuristic problem to be checked. (a list of vehicle objects)
    to_fulfilled: the number of requests that need to be fulfilled.
    """

    fulfilled = 0
    for v in solution:
        for p in v.path:
            if p.type == 2:
                fulfilled = fulfilled + 1
    return fulfilled >= to_fulfilled


def satisfy_one_more_customer(solution, customers):
    """
    This function satisfies one more customer request.
    The next unfulfilled customer request is simply inserted into each vehicle without splitting pairs. Therefore, this function
    returns len(solution) * len(vehicle.path)/2 different solutions in C.

    solution: the incomplete solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    """

    C = []
    for customer in customers:
        if find_vehicle(solution, customer.pickup) is None:
            # add points to a vehicle path
            for vehicle_target in solution:
                for p in range(0, len(vehicle_target.path), 2):
                    c = copy.deepcopy(solution)
                    v = c[vehicle_target.index]
                    v.add_section_path_after(v.path[p], customer.pickup)
                    v.add_section_path_after(customer.pickup, customer.dropoff)
                    if is_valid(v):
                        C.append(c)
            return C
    return C


def is_prefix(unfinished_solution, solution):
    """
    This function returns whether unfinished solution is a prefix of solution.
    Unfinished solution is a prefix of solution if every position of each point in every path is the same as in solution.

    unfinished_solution: the incomplete solution of the heuristic problem. (a list of vehicle objects)
    solution: The complete solution returned by the greedy construction heuristic.
    """

    for v_i in unfinished_solution:
        for v_j in solution:
            if not all(a == b for a, b in zip(v_i.path, v_j.path)):
                return False
    return True
