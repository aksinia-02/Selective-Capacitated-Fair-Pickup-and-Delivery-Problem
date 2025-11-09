from tools import *
from heuristics import construction
import copy


def solve(customers, vehicles, to_fulfilled, rho):

    x = copy.deepcopy(vehicles)
    x_best = None

    while not is_complete(x, to_fulfilled):
        C = satisfy_one_more_customer(x, customers)
        c_best = None

        for c in C:
            if x_best is None or not is_prefix(c, x_best):
                x_temp = construction.solve(customers, c, to_fulfilled, rho)
            else:
                x_temp = x_best
            if x_best is None or objective_function(x_temp, rho) < objective_function(x_best, rho):
                x_best = x_temp
                c_best = c
        x = c_best
    return x


def is_complete(solution, to_fulfilled):
    fulfilled = 0
    for v in solution:
        for p in v.path:
            if p.type == 2:
                fulfilled = fulfilled + 1
    return fulfilled >= to_fulfilled

def satisfy_one_more_customer(solution, customers):
    C = []

    for customer in customers:
        if find_vehicle(solution, customer.pickup) is None:
            c = copy.deepcopy(solution)

            # add points to a vehicle path
            for vehicle_target in solution:
                for i in range(0, len(vehicle_target.path)):
                    for j in range(i, len(vehicle_target.path)):
                        c_ij = copy.deepcopy(c)
                        v = c_ij[vehicle_target.index]
                        v.add_section_path_after(v.path[i], customer.pickup)
                        v.add_section_path_after(v.path[j+1], customer.dropoff)
                        if is_valid(v):
                            C.append(c_ij)
    return C

def is_prefix(unfinished_solution, solution):
    for v_i in unfinished_solution:
        for v_j in solution:
            if not all(a == b for a, b in zip(v_i.path, v_j.path)):
                return False
    return True
