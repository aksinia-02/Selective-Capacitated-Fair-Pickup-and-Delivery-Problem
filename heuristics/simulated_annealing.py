from tools import *
from heuristics import construction
from typing import Dict
import random
from classes.Vehicle import Vehicle

from classes.ObjectiveTracker import ObjectiveTracker

def group_customers_by_vehicle(customer_to_vehicle):
    vehicle_to_customers = {}

    for customer, vehicle in customer_to_vehicle.items():
        if vehicle not in vehicle_to_customers:
            vehicle_to_customers[vehicle] = []
        vehicle_to_customers[vehicle].append(customer)

    return vehicle_to_customers

def reorder_path(vehicle, path, n):

    depot = vehicle.path[0]

    unselected_locations = [p for p in path if p.type == 2]
    dropoffs = [p for p in path if p.type == 3]

    while unselected_locations:
        feasible = [loc for loc in unselected_locations if vehicle.load + loc.goods <= vehicle.capacity]
        if not feasible:
            unselected_locations.extend([d for d in dropoffs if d.index == n + vehicle.position.index])
        else:
            nearest_location = min(feasible, key=lambda loc: vehicle.position.calculate_distance(loc))
            vehicle.add_section_path(nearest_location)
            unselected_locations.remove(nearest_location)
            unselected_locations.extend([d for d in dropoffs if d.index == n + nearest_location.index])
    vehicle.add_section_path(depot)
    ids = [p.index for p in vehicle.path if p.index != 0]
    if len(ids) != len(set(ids)):
            print("❌ Duplicate point IDs found:", [x for x in ids if ids.count(x) > 1])
    return vehicle

def swap_two_customers(x, cust1, cust2, veh1, veh2, n):

    result_vehicles = x.copy()

    print(f"Swap {cust1.index} with {cust2.index} with vehicles {veh1} and {veh2}")

    vehicle_1 = x[veh1].copy() if veh1 < len(x) else None
    vehicle_2 = x[veh2].copy() if veh2 < len(x) else None

    pickup_c1 = cust1.pickup
    dropoff_c1 = cust1.dropoff
    pickup_c2 = cust2.pickup
    dropoff_c2 = cust2.dropoff

    new_vehicle_1 = new_vehicle_2 = None

    if vehicle_1 is not None:
        new_path = []

        for point in vehicle_1.path[1:-1]:
            if point != pickup_c1 and point != dropoff_c1:
                new_path.append(point)
        new_path.append(pickup_c2)
        new_path.append(dropoff_c2)

        print(vehicle_1.path_length)
        new_vehicle_1 = Vehicle(vehicle_1.index, vehicle_1.capacity, vehicle_1.position)
        new_vehicle_1 = reorder_path(new_vehicle_1, new_path, n)
        print(new_vehicle_1.path_length)

    if vehicle_2 is not None:
        new_path = []

        for point in vehicle_2.path[1:-1]:
            if point != pickup_c2 and point != dropoff_c2:
                new_path.append(point)
        new_path.append(pickup_c1)
        new_path.append(dropoff_c1)

        new_vehicle_2= Vehicle(vehicle_2.index, vehicle_2.capacity, vehicle_2.position)
        new_vehicle_2 = reorder_path(new_vehicle_2, new_path, n)

    if new_vehicle_1:
        result_vehicles[veh1] = new_vehicle_1
    if new_vehicle_2:
        result_vehicles[veh2] = new_vehicle_2
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
    delta_avg = estimate_average_delta(x, customers, customer_to_vehicle, n, k=50, rho=rho)
    T_init = -delta_avg / math.log(P0)
    return T_init

def simulated_annealing(x0, customers, customer_to_vehicle, n, rho, alpha=0.95, Tmin=1e-3, max_iters=50000):

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
                print(f"new solution with lenght {f_new} accepted")

            else:
                P = random.random()
                acceptance_prob = math.exp(-delta / T)

                if P < acceptance_prob:
                    x = x_new
                    f_x = f_new
                    tracker = tracker_new
                    print(f"new solution with lenght {f_new} accepted")

            iters += 1
            if iters >= max_iters:
                break

            print(f"iter: {iters}")
            if iters == 12:
                return x

        T = T * alpha
        print(f"T cooled to {T:.4f}, cost = {f_x:.2f}")

    print(f"Finished SA: iterations={iters}, final T={T:.5f}, best cost={f_x:.3f}")
    return x
    

def solve(customers, vehicles, to_fulfilled, rho):

    global objectiveTracker
    x = construction.solve(customers, vehicles, to_fulfilled, rho)
    x = reorder_paths(x, len(customers))
    return x

    # customer_to_vehicle: Dict[int, int] = {}

    # for i, vehicle in enumerate(x):
    #         for p in vehicle.path:
    #             if p.type == 2:
    #                 customer_to_vehicle[p.index] = i

    # objectiveTracker = ObjectiveTracker(x, rho)

    # print("Running simulated annealing")
    # return simulated_annealing(x, customers, customer_to_vehicle, len(customers), rho, 0.95, 1e-3, 50000)