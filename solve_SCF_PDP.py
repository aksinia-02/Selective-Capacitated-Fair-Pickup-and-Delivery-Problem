import argparse
import itertools
import networkx as nx

from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from display_solution import display_graph
from heuristics import greedy_randomized_adaptive_search_procedure

from heuristics.construction import solve as construction
from heuristics.randomized_construction import solve as randomized_construction
from heuristics.pilot_search import solve as pilot_search
from heuristics.local_search import solve as local_search
from heuristics.variable_neighborhood_descent import solve as variable_neighborhood_descent
from heuristics.greedy_randomized_adaptive_search_procedure import solve as greedy_randomized_adaptive_search_procedure
from tools import *

def read_input_file(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    n, n_k, C, to_fullfilled = map(int, lines[0].split()[:4])
    rho = float(lines[0].split()[4])
    
    demants_line = lines.index("# demands")
    demands = list(map(int, lines[demants_line + 1].split()))

    loc_line = lines.index("# request locations")
    locations = [tuple(map(int, line.split())) for line in lines[loc_line + 1:]]

    depot = locations[0]
    depot_point = Point(depot[0], depot[1], 0, 1, 0)
    vehicles = [Vehicle(i, C, depot_point) for i in range(n_k)]

    pickups = [(i, loc) for i, loc in enumerate(locations[1: n + 2], start=1)]
    dropoffs = [(i, loc) for i, loc in enumerate(locations[n + 1: 2 * n + 2], start=n + 1)]

    customers = [Customer(i, Point(pick[1][0], pick[1][1], pick[0], 2, d), Point(drop[1][0], drop[1][1], drop[0], 3, -d), d) for i, (pick, drop, d) in enumerate(zip(pickups, dropoffs, demands))]

    print(f"At least {to_fullfilled} of {n} requests must be fullfilled by using {n_k} vehicles.")
    return to_fullfilled, rho, vehicles, customers

def create_graph(depot, customers):

    graph = nx.Graph()

    nodes = [depot] + [c.pickup for c in customers] + [c.dropoff for c in customers]
    graph.add_nodes_from(nodes)

    for u, v in itertools.combinations(nodes, 2):
        distance = u.calculate_distance(v)
        graph.add_edge(u, v, weight=distance)

    return graph


def main():

    parser = argparse.ArgumentParser(description="Solving Selective Capacitated Fair Pickup and Delivery Problem.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file")

    args = parser.parse_args()
    print(args)

    print("\nSelect a type of heuristic:")
    print("c: construction heuristic\nrc: randomized construction heuristic\nps: pilot search\nls: local search\nvnd: variable neighborhood descent\ngrasp: greedy randomized adaptive search procedure\n TODO: add more")

    flag = True
    while flag:
        heuristic_type = input("Enter your choice (c/rc/ps/ls/vnd/grasp): ").strip().lower()
        if heuristic_type not in {'c', 'rc', 'ps', 'ls', 'vnd', 'grasp'}:
            print("Invalid input: please select one of: c, rc, ps, ls, vnd, grasp")
        else:
            flag = False

    switcher = {
        "c": construction,
        "rc": randomized_construction,
        "ps": pilot_search,
        "ls": local_search,
        "vnd": variable_neighborhood_descent,
        "grasp": greedy_randomized_adaptive_search_procedure
    }

    to_fullfilled, rho, vehicles, customers = read_input_file(args.input)
    graph = create_graph(vehicles[0].position, customers)

    result = switcher.get(heuristic_type, lambda: "unknown")(customers, vehicles, to_fullfilled, rho)

    obj_func = round(objective_function(result, rho), 2)
    display_graph(graph, result, obj_func)

    return



if __name__ == "__main__":
    main()