from classes.Statistic import Statistic
from tools import *
from heuristics import construction
import copy


def solve(customers, vehicles, to_fulfilled, rho, strategy="light", output_statistic=False):
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
        C = satisfy_one_more_customer(x, customers, strategy)
        c_best = None

        for c in C:
            if x_best is None or not is_prefix(c, x_best):
                x_temp = construction.solve(customers, copy.deepcopy(c), to_fulfilled, rho)
            else:
                x_temp = x_best
            if x_best is None or objective_function(x_temp, rho) < objective_function(x_best, rho):
                x_best = x_temp
                c_best = c
        x = c_best
        statistic.update(x_best, rho)
        if x is None:
            if output_statistic:
                return x_best, statistic
            else:
                return x_best
    if output_statistic:
        return x, statistic
    else:
        return x


def satisfy_one_more_customer(solution, customers, strategy):
    """
    This function satisfies one more customer request depending on the strategy.

    solution: the incomplete solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    strategy: "light" or "intensive".
    """

    if strategy == "light":
        return satisfy_one_more_customer_light(solution, customers)
    elif strategy == "intensive":
        return satisfy_one_more_customer_intensive(solution, customers)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


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


def satisfy_one_more_customer_light(solution, customers):
    """
    This function satisfies one more customer request following the light strategy.
    The next unfulfilled customer request is simply appended to each vehicle. Therefore, this function
    returns len(solution) different solutions in C.

    solution: the incomplete solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    """

    C = []
    for customer in customers:
        if find_vehicle(solution, customer.pickup) is None:
            # add points to a vehicle path
            for vehicle_target in solution:
                c = copy.deepcopy(solution)
                v = c[vehicle_target.index]
                v.add_section_path(customer.pickup)
                v.add_section_path(customer.dropoff)
                if is_valid(v):
                    C.append(c)
            return C
    return C


def satisfy_one_more_customer_intensive(solution, customers):
    """
    This function satisfies one more customer request following the intensive strategy.
    From each unfulfilled customer request the dropoff point is simply appended to each vehicle and the pickup point is
    placed at every possible space before the dropoff point. Therefore, this function
    returns len(customers) * len(solution) * len(vehicle.path) different solutions in C.

    solution: the incomplete solution of the heuristic problem. (a list of vehicle objects)
    customers: is a list of customer objects, each customer object contains information about a customer request.
    """

    C = []
    for customer in customers:
        if find_vehicle(solution, customer.pickup) is None:
            # add points to a vehicle path
            for vehicle_target in solution:
                for p in vehicle_target.path:
                    c = copy.deepcopy(solution)
                    v = c[vehicle_target.index]
                    v.add_section_path(customer.dropoff)
                    v.add_section_path_after(p, customer.pickup)
                    if is_valid(v):
                        C.append(c)
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
