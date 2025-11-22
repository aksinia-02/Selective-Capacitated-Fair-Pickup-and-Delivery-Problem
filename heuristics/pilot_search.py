from tools import *
from heuristics import construction
import copy


def solve(customers, vehicles, to_fulfilled, rho, strategy="light"):

    x = copy.deepcopy(vehicles)
    x_best = None

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
        if x is None:
            return x_best
    return x

def satisfy_one_more_customer(solution, customers, strategy):
    if strategy == "light":
        return satisfy_one_more_customer_light(solution, customers)
    elif strategy == "intensive":
        return satisfy_one_more_customer_intensive(solution, customers)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def is_complete(solution, to_fulfilled):
    fulfilled = 0
    for v in solution:
        for p in v.path:
            if p.type == 2:
                fulfilled = fulfilled + 1
    return fulfilled >= to_fulfilled


def satisfy_one_more_customer_light(solution, customers):
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
    for v_i in unfinished_solution:
        for v_j in solution:
            if not all(a == b for a, b in zip(v_i.path, v_j.path)):
                return False
    return True
