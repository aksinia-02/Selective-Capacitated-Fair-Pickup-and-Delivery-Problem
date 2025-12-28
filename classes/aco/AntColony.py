from classes.aco.Ant import Ant

import copy
import math

class AntColony:

    def __init__(self, graph, alpha, beta, initial_solution, to_fulfilled, func_objective, maximize, rho):
        self.graph = graph
        self.to_fulfilled = to_fulfilled
        self.n_customers = (len(graph.nodes()) - 1) // 2
        Ant.init_static_class_variables(graph, self.n_customers, alpha, beta)
        self.solution = copy.deepcopy(initial_solution)
        self.n_vehicles = len(self.solution)
        self.ants = self.create_ants(self.solution, graph)
        self.func_objective = func_objective
        self.rho = rho
        self.maximize = maximize

    def create_ants(self, vehicles, graph):
        n_ants = len(vehicles)

        ants = []
        for i in range(n_ants):
            ants.append(Ant(i, 0.2, vehicles[i]))
        return ants
    
    def construct_solution(self):
        active_ants_counter = self.n_vehicles

        while (active_ants_counter > 0) and self.to_fulfilled > 0:
            best_obj = 0 if self.maximize else math.inf  
            best_next = None
            best_ant = 0
            for i, ant in enumerate(self.ants):
                if ant.active:
                    next_node, weight = ant.get_next_step()
                    ant.vehicle.path_length += weight
                    objective = self.func_objective(self.solution, self.rho)
                    if (self.maximize and objective > best_obj) or (not self.maximize and objective < best_obj):
                        best_obj = objective
                        best_next = copy.deepcopy(next_node)
                        best_ant = i
                    ant.vehicle.path_length -= weight
            for i, ant in enumerate(self.ants):
                if i == best_ant:
                    if ant.next_node.index <= self.n_customers:
                        self.to_fulfilled -= 1
                    completed_path = ant.make_step()
                else:
                    completed_path = ant.delete_assigned_node(best_next)
                if completed_path:
                    active_ants_counter -= 1
                    ant.active = False

        depot = self.solution[0].path[0]
        for vehicle in self.solution:
            vehicle.add_section_path(depot, self.graph[vehicle.position][depot]["weight"])
        return self.solution
            