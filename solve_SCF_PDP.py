import argparse
import itertools
import networkx as nx

from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from display_solution import display_graph

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
    depot_point = Point(depot[0], depot[1], 0, 1)
    vehicles = [Vehicle(C, depot_point) for _ in range(n_k)]

    pickups = [(i, loc) for i, loc in enumerate(locations[1: n + 2], start=1)]
    dropoffs = [(i, loc) for i, loc in enumerate(locations[n + 1: 2 * n + 2], start=n + 1)]

    customers = [Customer(Point(pick[1][0], pick[1][1], pick[0], 2), Point(drop[1][0], drop[1][1], drop[0], 3), d) for pick, drop, d in zip(pickups, dropoffs, demands)]

    print(f"At least {to_fullfilled} of {n} requests must be fullfilled by using {n_k} vehicles.")
    return to_fullfilled, rho, C, vehicles, customers

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
    display_graph(graph)


def main():

    parser = argparse.ArgumentParser(description="Solving Selective Capacitated Fair Pickup and Delivery Problem.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file")

    args = parser.parse_args()
    print(args)

    to_fullfilled, rho, C, vehicles, customers = read_input_file(args.input)
    create_graph(vehicles[0].position, customers)

    return

    min_function = math.inf 

    # after each step
    total = sum(v.path_length for v in vehicles)
    squares = sum(v.path_length ** 2 for v in vehicles)
    jain_fairness = (total ** 2) / (len(vehicles) * squares)

    function = total + rho * (1 - jain_fairness)

    print(jain_fairness)



if __name__ == "__main__":
    main()