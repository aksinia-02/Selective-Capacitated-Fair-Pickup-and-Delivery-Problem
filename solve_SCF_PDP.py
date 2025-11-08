import argparse
import itertools
import networkx as nx

from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from display_solution import display_graph

from heuristics.construction import solve as construction
from heuristics.randomized_construction import solve as randomized_construction
from heuristics.local_search import solve as local_search

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

    # graph.add_weighted_edges_from([
    #     (depot, c.pickup, depot.calculate_distance(c.pickup))
    #     for c in customers
    # ] + [
    #     (depot, c.dropoff, depot.calculate_distance(c.dropoff))
    #     for c in customers
    # ])
    #display_graph(graph)
    return graph


def main():

    parser = argparse.ArgumentParser(description="Solving Selective Capacitated Fair Pickup and Delivery Problem.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file")

    args = parser.parse_args()
    print(args)

    print("\nSelect a type of heuristic:")
    print("c: construction heuristic\nrc:  randomized construction heuristic\n TODO: add more")

    flag = True
    while flag:
        heuristic_type = input("Enter your choice (c/rc/ls): ").strip().lower()
        if heuristic_type not in {'c', 'rc', 'ls'}:
            print("Invalid input: please select one of: c, rc, ls")
        else:
            flag = False

    switcher = {
        "c": construction,
        "rc": randomized_construction,
        "ls": local_search
    }

    to_fullfilled, rho, vehicles, customers = read_input_file(args.input)
    graph = create_graph(vehicles[0].position, customers)

    result = switcher.get(heuristic_type, lambda: "unknown")(customers, vehicles, to_fullfilled, rho)
    #print(result)

    #display_graph(graph, result)

    return

    min_function = math.inf 



if __name__ == "__main__":
    main()