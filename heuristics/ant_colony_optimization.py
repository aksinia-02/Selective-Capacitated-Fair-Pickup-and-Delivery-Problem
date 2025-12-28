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
import copy
import math

def solve(customers, initial_solution, to_fulfilled, graph, n_colonies, alpha, beta, evaporation, rho, obj_name):

    switcher = {
        "min_max": (max_min_fairness, True),
        "gini": (gini_coefficient, True),
        "jain": (objective_function, False)
    }

    func, maximize = switcher[obj_name]

    visualization = LiveGraph(graph)
    fill_world_representation(graph)

    global_best_colony = None
    global_max_obj = 0 if maximize else math.inf

    for _ in range(100):

        evaporate_pheromone(graph, evaporation)

        best_colony = None
        best_obj = 0 if maximize else math.inf  
        for _ in range(n_colonies):
            ant_colony = AntColony(graph, alpha, beta, initial_solution, to_fulfilled, func, maximize, rho)
            solution = ant_colony.construct_solution()
            #ant.construct_soltution(initial_solution)
            new_objective = func(solution, rho)
            if (maximize and new_objective > best_obj) or (not maximize and new_objective < best_obj):
                best_colony = copy.deepcopy(ant_colony)
                best_obj = new_objective

        deposit_pheromone(graph, best_colony)

        if (maximize and best_obj > global_max_obj) or (not maximize and best_obj < global_max_obj):
            global_best_colony = copy.deepcopy(best_colony)
            global_max_obj = best_obj
            print(f"global_best_obj {best_obj} is found!")

        visualization.handle_events()
        visualization.render(graph)
        time.sleep(0.05)

    # while True:
    #     visualization.handle_events()
    #     visualization.render(graph)
    #     time.sleep(0.05)


    return global_best_colony.solution


def fill_world_representation(graph):

    for u, v in list(graph.edges()):
        graph[u][v]["width"] = random.randint(1, 4)
        graph[u][v]["color"] = (220, 220, 220)
        graph[u][v]["scent"] = 0.2

def evaporate_pheromone(graph, rho, tau_min=1e-4):
    for u, v in graph.edges():
        graph[u][v]["scent"] *= (1 - rho)
        if graph[u][v]["scent"] < tau_min:
            graph[u][v]["scent"] = tau_min

def deposit_pheromone(graph, best_colony):
    for j, vehicle in enumerate(best_colony.solution):
        path_length = len(vehicle.path)
        color = best_colony.ants[j].color
        for i, node in enumerate(vehicle.path):
            if i != path_length - 1:
                next_node = vehicle.path[i + 1]
                delta = 1 / max(graph[node][next_node]["weight"], 1e-6)
                graph[node][next_node]["scent"] += delta
                graph[node][next_node]["scent"] = min(graph[node][next_node]["scent"], 5)
                graph[node][next_node]["color"] = color
