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

    for i in range(100):
        print(f"step {i}")

        #evaporate_pheromone(graph, evaporation)

        best_colony = None
        best_obj = 0 if maximize else math.inf  

        all_colonies = []

        for _ in range(n_colonies):
            ant_colony = AntColony(graph, alpha, beta, initial_solution, to_fulfilled, func, maximize, rho)
            solution = ant_colony.construct_solution()
            all_colonies.append(ant_colony)
            new_objective = func(solution, rho)
            if (maximize and new_objective > best_obj) or (not maximize and new_objective < best_obj):
                best_colony = copy.deepcopy(ant_colony)
                best_obj = new_objective

        if (maximize and best_obj > global_max_obj) or (not maximize and best_obj < global_max_obj):
            global_best_colony = copy.deepcopy(best_colony)
            global_max_obj = best_obj
            print(f"global_best_obj {best_obj} is found!")

        deposit_pheromone_rank_based(graph, all_colonies, rho=evaporation, w=int(n_colonies/2), best_colony=best_colony, maximize=maximize)
        global_max_tau = max(graph[u][v]["scent"] for u, v in graph.edges())
        update_edge_colors(graph, tau_min=1e-4, tau_max=global_max_tau)

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

def evaporate_pheromone(graph, evaporation, tau_min=1e-4):
    for u, v in graph.edges():
        graph[u][v]["scent"] *= (1 - evaporation)
        if graph[u][v]["scent"] < tau_min:
            graph[u][v]["scent"] = tau_min

def update_edge_colors(graph, tau_min, tau_max):
    for u, v in graph.edges():
        tau = graph[u][v]["scent"]
        t = (tau - tau_min) / (tau_max - tau_min)
        t = max(0.0, min(1.0, t))

        red  = int(255 * t)
        blue = int(255 * (1 - t))

        graph[u][v]["color"] = (red, 0, blue)

def deposit_pheromone_rank_based(graph, all_colonies, rho, w, best_colony, maximize):
    """
    Rank-Based Ant System (Bullnheimer, 1999)
    Ranking is done by objective value
    """

    # Evaporation
    for u, v in graph.edges():
        graph[u][v]["scent"] *= (1 - rho)

    # Rank ants by objective value
    all_colonies.sort(key=lambda c: c.final_objective,reverse=maximize)

    # Deposit pheromone from top (w-1) ants
    for r, colony in enumerate(all_colonies[:w], start=1):
        weight = w - r
        for ant in colony.ants:

            vehicle = ant.vehicle
            delta = weight * 500 / vehicle.path_length

            path = vehicle.path
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                graph[u][v]["scent"] += delta
                #graph[u][v]["scent"] = max(5.0, graph[u][v]["scent"])
