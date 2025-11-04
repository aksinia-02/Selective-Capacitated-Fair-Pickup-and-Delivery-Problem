import math

def objective_function(vehicles, rho):
    total = sum(v.path_length for v in vehicles)
    squares = sum(v.path_length ** 2 for v in vehicles)
    jain_fairness = (total ** 2) / (len(vehicles) * squares)

    objective = total + rho * (1 - jain_fairness)

    return objective