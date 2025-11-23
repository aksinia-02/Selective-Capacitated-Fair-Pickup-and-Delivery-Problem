from tools import *
from heuristics import construction
from typing import Dict
import random
from classes.Vehicle import Vehicle
import math
import copy

from classes.ObjectiveTracker import ObjectiveTracker

def group_customers_by_vehicle(customer_to_vehicle):
    vehicle_to_customers = {}

    for customer, vehicle in customer_to_vehicle.items():
        if vehicle not in vehicle_to_customers:
            vehicle_to_customers[vehicle] = []
        vehicle_to_customers[vehicle].append(customer)

    return vehicle_to_customers

def best_insertion(vehicle, customer):

    path = vehicle.path

    #print(f"path: {path}")
    #print(f"to insert: {customer.pickup}, {customer.dropoff}")

    best_cost = float("inf")
    best_before_P, best_before_D = None, None

    path_len = len(path)

    load = [0] * (path_len)
    cur = 0
    #print(path_len)
    for k in range(path_len):
        cur += path[k].goods
        load[k] = cur
    #print(load)

    # try all positions for pickup insertion
    for i in range(path_len - 1):
        #print(f"i: {i}")
        if load[i] + customer.goods > vehicle.capacity:
            continue

        # try all dropoff positions
        for j in range(i+1, path_len):
            #print(f"j: {j}")

            # simulate path load from new pickup to new dropoff
            feasible = True
            curload = load[i] + customer.goods
            for k in range(i, j):
                curload += path[k].goods
                #print(f"cur: {curload}")
                if curload > vehicle.capacity:
                    feasible = False
                    #print(f"curload > capacity: {curload}")
                    break

            if not feasible:
                continue

            # Insert pickup
            before_P = path[i]
            if abs(i-j) == 1:
                after_P = customer.dropoff
            else:
                after_P = path[i+1]

            #print(f"P: before: {before_P}, pickup: {customer.pickup}, after: {after_P}")

            delta_pickup = before_P.calculate_distance(customer.pickup) + after_P.calculate_distance(customer.pickup)- after_P.calculate_distance(before_P)

            if abs(i-j) == 1:
                before_D = customer.pickup
            else:
                before_D = path[j-1]
            after_D = path[j]

            #print(f"D: before: {before_D}, dropoff: {customer.dropoff}, after: {after_D}")

            delta_dropoff = before_D.calculate_distance(customer.dropoff) + after_D.calculate_distance(customer.dropoff)- after_D.calculate_distance(before_D)

            delta = delta_pickup + delta_dropoff
            #print(f"delta: {delta}")

            if delta < best_cost:
                best_cost = delta
                best_before_P, best_before_D = before_P, before_D

    # Build new path
    vehicle.simple_add_point_after(best_before_P, customer.pickup)
    vehicle.simple_add_point_after(best_before_D, customer.dropoff)
    if vehicle.path_length < 0:
        return None

    return vehicle


def swap_two_customers(x, cust1, cust2, veh1, veh2, n):

    result_vehicles = copy.deepcopy(x)

    #print(f"Swap {cust1.index} with {cust2.index} with vehicles {veh1} and {veh2}")

    vehicle_1 = result_vehicles[veh1] if veh1 < len(x) else None
    vehicle_2 = result_vehicles[veh2] if veh2 < len(x) else None

    pickup_c1 = cust1.pickup
    dropoff_c1 = cust1.dropoff
    pickup_c2 = cust2.pickup
    dropoff_c2 = cust2.dropoff

    if vehicle_1 is not None:
        vehicle_1.simple_remove_point(cust1.pickup)
        vehicle_1.simple_remove_point(cust1.dropoff)
        vehicle_1 = best_insertion(vehicle_1, cust1)
    if vehicle_2 is not None:
        vehicle_2.simple_remove_point(cust2.pickup)
        vehicle_2.simple_remove_point(cust2.dropoff)
        vehicle_2 = best_insertion(vehicle_2, cust2)

    if vehicle_1:
        result_vehicles[veh1] = vehicle_1
    if vehicle_2:
        result_vehicles[veh2] = vehicle_2
    return result_vehicles


def random_choose_swap_two_customers(x, customers, customer_to_vehicle, n):

    vehicle_to_customers = group_customers_by_vehicle(customer_to_vehicle)
    not_fullfilled = set(range(1, n + 1)) - set(customer_to_vehicle.keys())
    vehicle_list = list(vehicle_to_customers.items()) + [(len(x), list(not_fullfilled))]

    (veh1, custs1), (veh2, custs2) = random.sample(vehicle_list, 2)

    c1 = random.choice(custs1)
    c2 = random.choice(custs2)

    cust1 = customers[c1 - 1]
    cust2 = customers[c2 - 1]

    return swap_two_customers(x, cust1, cust2, veh1, veh2, n)

def estimate_average_delta(x, customers, customer_to_vehicle, n, k=30, rho=1):

    deltas = []

    for _ in range(k):
        x_new = random_choose_swap_two_customers(x, customers, customer_to_vehicle, n)
        f_old = ObjectiveTracker(x, rho).compute_objective()
        f_new = ObjectiveTracker(x_new, rho).compute_objective()
        delta = f_new - f_old
        if delta > 0:
            deltas.append(delta)

    if not deltas:
        return 1.0

    return sum(deltas) / len(deltas)

def compute_initial_temperature(x, customers, customer_to_vehicle, n, rho=1, P0=0.03):
    """
    Computes the initial temperature T_init for SA.
    P0 = initial acceptance probability for worse moves (0.03 = 3%)
    """
    delta_avg = estimate_average_delta(x, customers, customer_to_vehicle, n, k=3, rho=rho)
    T_init = -delta_avg / math.log(P0)
    return T_init

def simulated_annealing(x0, customers, customer_to_vehicle, n, rho, alpha=0.95, Tmin=1e-3, max_iters=1000):

    x = x0
    tracker = ObjectiveTracker(x, rho)
    f_x = tracker.compute_objective()
    print(f"initial solution with lenght {f_x}")

    T = compute_initial_temperature(x, customers, customer_to_vehicle, n, rho)
    print(f"Initial temperature = {T:.4f}")

    neighborhood_size = n * (n - 1) / 2
    equilibrium = int(neighborhood_size / 4)
    print(f"equilibrium: {equilibrium}")

    iters = 0

    while T > Tmin and iters < max_iters:

        for _ in range(equilibrium):

            x_new = random_choose_swap_two_customers(x, customers, customer_to_vehicle, n)
            tracker_new = ObjectiveTracker(x_new, rho)
            f_new = tracker_new.compute_objective()

            delta = f_new - f_x

            if delta < 0:
                x = x_new
                f_x = f_new
                tracker = tracker_new
                #print(f"new solution with lenght {f_new} accepted")

            else:
                P = random.random()
                acceptance_prob = math.exp(-delta / T)

                if P < acceptance_prob:
                    x = x_new
                    f_x = f_new
                    tracker = tracker_new
                    #print(f"new solution with lenght {f_new} accepted")

            iters += 1
            if iters >= max_iters:
                break

        T = T * alpha
        print(f"T cooled to {T:.4f}, objective value = {f_x:.2f}")

    print(f"Finished SA: iterations={iters}, final T={T:.5f}, objective value={f_x:.3f}")
    return x
    

def solve(customers, vehicles, to_fulfilled, rho):

    global objectiveTracker
    x = construction.solve(customers, vehicles, to_fulfilled, rho)
    x = reorder_paths(x, len(customers))

    customer_to_vehicle: Dict[int, int] = {}

    for i, vehicle in enumerate(x):
            for p in vehicle.path:
                if p.type == 2:
                    customer_to_vehicle[p.index] = i

    objectiveTracker = ObjectiveTracker(x, rho)

    print("Running simulated annealing")
    return simulated_annealing(x, customers, customer_to_vehicle, len(customers), rho, 0.95, 1e-3, 50000)