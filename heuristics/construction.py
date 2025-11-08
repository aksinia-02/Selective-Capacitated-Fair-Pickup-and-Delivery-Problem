from typing import List
import math
import itertools

from classes.Point import Point
from classes.Customer import Customer
from classes.Vehicle import Vehicle

from tools import objective_function


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

def total_distance(sequence):
    distance = 0
    for i in range(len(sequence) - 1):
        distance += sequence[i].calculate_distance(sequence[i + 1])
    return distance


def solve(customers, vehicles, to_fullfilled, rho):

    depot = vehicles[0].position

    #customers = sort_customers(depot, customers)

    min_function = math.inf
    sorted_pairs = calculate_savings(customers, depot)

    temp_vehicles = [Vehicle(i, vehicles[0].capacity, depot) for i in range(len(customers))]

    for i in range(len(customers)):
        temp_vehicles[i].add_section_path(customers[i].pickup, customers[i].goods)
        temp_vehicles[i].add_section_path(customers[i].dropoff, -customers[i].goods)
        temp_vehicles[i].add_section_path(depot)
        
    for (i, j), saving in sorted_pairs:

        vehicle_index_i = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == i for p in v.path)), None)
        vehicle_index_j = next((idx for idx, v in enumerate(temp_vehicles) if any(p.index == j for p in v.path)), None)
        
        if vehicle_index_i is not None and vehicle_index_j is not None and vehicle_index_i != vehicle_index_j:
            if temp_vehicles[vehicle_index_i].get_available_capacity_at_position_x(customers[vehicle_index_i].pickup) + customers[vehicle_index_i].goods >= temp_vehicles[vehicle_index_j].load:

                P1, D1 = customers[vehicle_index_i].pickup, customers[vehicle_index_i].dropoff
                P2, D2 = customers[vehicle_index_j].pickup, customers[vehicle_index_j].dropoff

                valid_sequences = [
                    [P1, D1, P2, D2],
                    [P1, P2, D1, D2],
                    [P1, P2, D2, D1],
                    [P2, D2, P1, D1],
                    [P2, P1, D2, D1],
                    [P2, P1, D1, D2],
                ]
                best_sequence = min(valid_sequences, key=total_distance)
                best_distance = total_distance(best_sequence)

                #print(f"Best sequence: {best_sequence}")
                #print(f"Current path: {temp_vehicles[vehicle_index_i].path}")


                # temp_vehicles[vehicle_index_i].add_section_path_after(customers[vehicle_index_i].pickup, customers[vehicle_index_j].pickup)
                # temp_vehicles[vehicle_index_i].load += customers[vehicle_index_i].goods
                if best_sequence[0] not in temp_vehicles[vehicle_index_i].path:
                    if best_sequence[1] not in temp_vehicles[vehicle_index_i].path:
                        temp_vehicles[vehicle_index_i].add_section_path_after(temp_vehicles[vehicle_index_i].get_location_before_x(best_sequence[2]), best_sequence[0], best_sequence[0].goods)
                        temp_vehicles[vehicle_index_i].add_section_path_after(best_sequence[0], best_sequence[1], best_sequence[1].goods)
                    else:
                        temp_vehicles[vehicle_index_i].add_section_path_before(best_sequence[1], best_sequence[0], best_sequence[0].goods)
                else:
                    temp_vehicles[vehicle_index_i].add_section_path_after(best_sequence[0], best_sequence[1], best_sequence[1].goods)
                #print(f"0-1 insert{temp_vehicles[vehicle_index_i].path}")

                if best_sequence[2] not in temp_vehicles[vehicle_index_i].path:
                    if best_sequence[3] not in temp_vehicles[vehicle_index_i].path:
                        temp_vehicles[vehicle_index_i].add_section_path_before(temp_vehicles[vehicle_index_i].get_location_after_x(best_sequence[1]), best_sequence[2], best_sequence[2].goods)
                        temp_vehicles[vehicle_index_i].add_section_path_after(best_sequence[2], best_sequence[3], best_sequence[3].goods)
                    else:
                        temp_vehicles[vehicle_index_i].add_section_path_before(best_sequence[3], best_sequence[2], best_sequence[2].goods)
                else:
                    temp_vehicles[vehicle_index_i].add_section_path_after(best_sequence[2], best_sequence[3], best_sequence[3].goods)
                # print(f"0-1 insert {temp_vehicles[vehicle_index_i].path}")
                # print("___________________")

                temp_vehicles[vehicle_index_j].path_length = 0
    temp_vehicles = [v for v in temp_vehicles if v.path_length > 0]
    #while len(temp_vehicles) != len(vehicles):

    print(len(temp_vehicles))
    for vehicle in temp_vehicles:
        print(vehicle)
    return temp_vehicles