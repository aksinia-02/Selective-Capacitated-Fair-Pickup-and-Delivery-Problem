from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from classes.ObjectiveTracker import ObjectiveTracker
from visualization.display_ant_colony import LiveGraph
from classes.aco.Ant import Ant
from classes.aco.AntColony import AntColony
from classes.Statistic import Statistic

from tools import objective_function

import random
import time
import copy
import math

def solve(
        customers, initial_solution, to_fulfilled, graph, n_colonies, alpha, beta, 
        evaporation, rho, obj_name, output_statistic=False, visualization=True
    ):

    statistic = Statistic()

    if visualization:
        visualization = LiveGraph(graph)
    fill_world_representation(graph)

    global_best_colony = None
    global_max_obj = math.inf

    for i in range(60):
        print(f"step {i}")

        best_colony = None
        best_obj = math.inf  

        all_colonies = []

        for i in range(n_colonies):
            ant_colony = AntColony(i, graph, alpha, beta, initial_solution, to_fulfilled, obj_name, rho)
            solution = ant_colony.construct_solution()
            all_colonies.append(ant_colony)
            new_objective = objective_function(solution, rho, obj_name)
            if new_objective < best_obj:
                best_colony = copy.deepcopy(ant_colony)
                best_obj = new_objective

        if best_obj < global_max_obj:
            global_best_colony = copy.deepcopy(best_colony)
            statistic.update(global_best_colony.solution, rho)
            global_max_obj = best_obj
            print(f"global_best_obj {best_obj} is found!")

        deposit_pheromone_rank_based(graph, all_colonies, rho=evaporation, w=int(n_colonies/2), best_colony=best_colony)
        global_max_tau = max(graph[u][v]["scent"] for u, v in graph.edges())
        update_edge_colors(graph, tau_min=1e-4, tau_max=global_max_tau)

        if visualization:
            visualization.handle_events()
            visualization.render(graph)
            time.sleep(0.05)

    # while True:
    #     visualization.handle_events()
    #     visualization.render(graph)
    #     time.sleep(0.05)

    if output_statistic:
        return global_best_colony.solution, statistic
    else:
        return global_best_colony.solution


def fill_world_representation(graph):

    for u, v in list(graph.edges()):
        graph[u][v]["width"] = random.randint(1, 4)
        graph[u][v]["color"] = (220, 220, 220)
        graph[u][v]["scent"] = 0.00001

def update_edge_colors(graph, tau_min, tau_max):
    for u, v in graph.edges():
        tau = graph[u][v]["scent"]
        t = (tau - tau_min) / (tau_max - tau_min)
        t = max(0.0, min(1.0, t))

        red  = int(255 * t)
        blue = int(255 * (1 - t))

        graph[u][v]["color"] = (red, 0, blue)

def normalized_objective(obj, obj_min, obj_max):
    return (obj - obj_min) / (obj_max - obj_min + 1e-9)

def deposit_pheromone_rank_based(graph, all_colonies, rho, w, best_colony):
    """
    Rank-Based Ant System (Bullnheimer, 1999)
    Ranking is done by objective value
    """
    Q = 1 

    objs = [c.final_objective for c in all_colonies]
    obj_min, obj_max = min(objs), max(objs)

    # Evaporation
    for u, v in graph.edges():
        graph[u][v]["scent"] *= (1 - rho)

    # Rank ants by objective value
    all_colonies.sort(key=lambda c: c.final_objective,reverse=False)

    w = max(3, min(w, len(all_colonies)))

    # Deposit pheromone from top (w-1) ants
    for r, colony in enumerate(all_colonies[:w]):
        weight = w - r
        quality = normalized_objective(colony.final_objective, obj_min, obj_max)
        for ant in colony.ants:

            vehicle = ant.vehicle
            delta = weight * Q * quality / (1 + 1e-4 * vehicle.path_length)

            path = vehicle.path
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                graph[u][v]["scent"] += delta
                #print(graph[u][v]["scent"])
                #graph[u][v]["scent"] = max(10.0, graph[u][v]["scent"])
