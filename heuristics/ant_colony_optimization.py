from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from classes.ObjectiveTracker import ObjectiveTracker
from visualization.display_ant_colony import LiveGraph
from classes.aco.Ant import Ant

import random
import time

def solve(customers, initial_solution, to_fulfilled, graph, n_ants, alpha, beta, rho):

    visualization = LiveGraph(graph)
    fill_world_representation(graph)
    Ant.alpha = alpha
    Ant.beta = beta
    ants = create_ants(n_ants, initial_solution[0].path[0], initial_solution[0].capacity, graph)

    for ant in ants:
        ant.make_step()
        ant.make_step()
        ant.make_step()
        print(ant)

    # for u, v in list(graph.edges()):
    #     print(graph[u][v]["scent"])


    while True:
        visualization.handle_events()

        visualization.render(graph)
        time.sleep(0.05)

def create_ants(n_ants, depot, capacity, graph):
    ants = []
    for i in range(n_ants):
        if i == 0:
            Ant.graph = graph
            Ant.n_customers = int((len(graph.nodes()) - 1) / 2)
        ants.append(Ant(i, 0.2, depot, capacity))
    return ants

def fill_world_representation(graph):

    for u, v in list(graph.edges()):
        graph[u][v]["width"] = random.randint(1, 4)
        graph[u][v]["color"] = (220, 220, 220)
        graph[u][v]["scent"] = 0.2

