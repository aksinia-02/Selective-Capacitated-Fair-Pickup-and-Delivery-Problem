from typing import List
import math
import itertools

from classes.Point import Point
from classes.Customer import Customer
from classes.Vehicle import Vehicle

from tools import jain_fairness


# def sort_customers(depot: Point, customers: List[Customer]):
#     scores = {customer.index: customer.goods / (customer.pickup.calculate_distance(depot) + customer.dropoff.calculate_distance(depot))
#               for customer in customers}
#     sorted_customers = sorted(customers, key=lambda c: scores[c.index], reverse=True)
#     # for customer in sorted_customers:
#     #     print(customer)
#     #     print(scores.get(customer.index))
#     return sorted_customers

def calculate_savings(customers, depot):
    """
    Calculate the Clarke-Wright savings for all pairs of customers
    S_ij = d(depot,i) + d(j,depot) - d(i,j)
    """
    savings = {}
    for i, j in itertools.combinations(range(len(customers)), 2):
        s = (depot.calculate_distance(customers[i].pickup) + depot.calculate_distance(customers[j].pickup) - customers[i].pickup.calculate_distance(customers[j].pickup))
        savings[(i, j)] = s
    return sorted(savings.items(), key=lambda x: x[1], reverse=True)


def solve(customers, vehicles, to_fullfilled, rho):

    depot = vehicles[0].position

    #customers = sort_customers(depot, customers)

    min_function = math.inf
    sorted_pairs = calculate_savings(customers, depot)

    temp_vehicles = [Vehicle(i, vehicles[0].capacity, depot) for i in range(len(customers))]

    for i in range(len(customers)):
        temp_vehicles[i].add_section_path(customers[i].pickup)
        temp_vehicles[i].add_section_path(customers[i].dropoff)
        temp_vehicles[i].add_section_path(depot)
        temp_vehicles[i].load = customers[i].goods
    for (i, j), saving in sorted_pairs:

        vehicle_index_i = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == i for p in v.path)), None)
        vehicle_index_j = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == j for p in v.path)), None)
        
        if vehicle_index_i is not None and vehicle_index_j is not None and vehicle_index_i != vehicle_index_j:
            if temp_vehicles[vehicle_index_i].available_capacity() >= temp_vehicles[vehicle_index_j].load:


                temp_vehicles[vehicle_index_i].add_section_path_between(customers[vehicle_index_i].pickup, customers[vehicle_index_j].pickup)
                temp_vehicles[vehicle_index_i].load += customers[vehicle_index_i].goods

                temp_vehicles[vehicle_index_j].path_length = 0
    temp_vehicles = [v for v in temp_vehicles if v.path_length > 0]
    for temp_vehicle in temp_vehicles:
        print(temp_vehicle.path)
        print(temp_vehicle.load)
            # if temp_vehicles[vehicle_index_i].available_capacity() >= temp_vehicles[vehicle_index_j].load:
            #     temp_vehicles[i].path_length += customers[i].pickup.calculate_distance()
            #     pass
            # Merge routes
            # new_route = route_i + route_j
            # routes.remove(route_i)
            # routes.remove(route_j)
            # routes.append(new_route)

    # for vehicle in vehicles:
    #     for customer in customers:
    #         if not customer.has_vehicle and vehicle.available_capacity() >= customer.goods:
    #             print(f"index: {vehicle.index}, capacity: {vehicle.available_capacity()}, customer goods: {customer.goods}")
    #             vehicle.add_section_path(customer.pickup)
    #             vehicle.load += customer.goods
    #             print(vehicle.path)
    #             customer.has_vehicle = True
    #             to_fullfilled -= 1

    return None