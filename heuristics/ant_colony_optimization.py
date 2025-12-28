from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from classes.ObjectiveTracker import ObjectiveTracker
from visualization.display_ant_colony import LiveGraph
from classes.aco.Ant import Ant
from classes.aco.AntColony import AntColony

from tools import max_min_fairness, gini_coefficient, objective_function

import random
import time

def solve(customers, initial_solution, to_fulfilled, graph, n_ants, alpha, beta, rho, obj_name):

    switcher = {
        "min_max": max_min_fairness,
        "gini": gini_coefficient,
        "jain": objective_function
    }

    func = switcher[obj_name]

    visualization = LiveGraph(graph)
    fill_world_representation(graph)
    ant_colony = AntColony(graph, alpha, beta, initial_solution, func)

    for _ in range(1):
        best_path = None
        max_quality = 0
        for _ in range(n_ants):
            ant_colony.construct_solution()
            #ant.construct_soltution(initial_solution)
            new_objective = max_min_fairness(initial_solution)
            if new_objective > max_quality:
                best_path = initial_solution
                max_quality = new_objective

    while True:
        visualization.handle_events()
        visualization.render(graph)
        time.sleep(0.05)

    # for ant in ants:
    #     ant.make_step()
    #     ant.make_step()
    #     ant.make_step()
    #     print(ant)

    # for u, v in list(graph.edges()):
    #     print(graph[u][v]["scent"])


    # for i in range(50):
    #     visualization.handle_events()
    #     for ant in ants:
    #         ant.make_step()

    #     visualization.render(graph)
    #     time.sleep(0.05)

def fill_world_representation(graph):

    for u, v in list(graph.edges()):
        graph[u][v]["width"] = random.randint(1, 4)
        graph[u][v]["color"] = (220, 220, 220)
        graph[u][v]["scent"] = 0.2

