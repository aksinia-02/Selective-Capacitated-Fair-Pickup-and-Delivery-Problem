from classes.Customer import Customer
from classes.Point import Point
from classes.Vehicle import Vehicle
from classes.ObjectiveTracker import ObjectiveTracker
from visualization.display_ant_colony import LiveGraph

import random
import time

def solve(customers, initial_solution, to_fulfilled, graph):


    visualization = LiveGraph(graph)

    while True:
        visualization.handle_events()

        # Simulate dynamic updates (future pheromones)
        u, v = random.choice(list(graph.edges()))
        graph[u][v]["width"] = random.randint(1, 4)
        graph[u][v]["color"] = (255, 100, 100)

        visualization.render()
        time.sleep(0.05)

