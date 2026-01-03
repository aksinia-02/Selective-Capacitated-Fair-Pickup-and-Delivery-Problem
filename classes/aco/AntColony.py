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
        self.active_ants_counter = self.n_vehicles
        self.must_clean = True
        self.final_objective = 0

    def create_ants(self, vehicles, graph):
        n_ants = len(vehicles)

        ants = []
        for i in range(n_ants):
            ants.append(Ant(i, 0.2, vehicles[i]))
        return ants
    
    def keep_depots_selected_pickupps(self):
        for ant in self.ants:
            completed_path = ant.clean_unused_customers()
            #print(f"{ant.index} cleaned: {completed_path}")
            if completed_path:
                    self.active_ants_counter -= 1
                    ant.active = False
    
    def construct_solution(self):

        while (self.active_ants_counter > 0):
            #print(f"to_fullfilled: {self.to_fulfilled}")
            if self.must_clean and (self.to_fulfilled == 0):
                self.keep_depots_selected_pickupps()
                self.must_clean = False
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
            #print(f"best ant {best_ant}, best next: {best_next}")

            for i, ant in enumerate(self.ants):
                if i == best_ant:
                    if ant.next_node.index <= self.n_customers:
                        if ant.next_node.type == 2:
                            self.to_fulfilled -= 1
                    completed_path = ant.make_step()
                    #ant.print_pos_next_nodes()
                    #print(completed_path)
                else:
                    if not ant.active:
                        completed_path = False
                    else:
                        completed_path = ant.delete_assigned_node(best_next)
                        #ant.print_pos_next_nodes()
                if completed_path:
                    self.active_ants_counter -= 1
                    ant.active = False
                #print(self.active_ants_counter)

        depot = self.solution[0].path[0]
        for vehicle in self.solution:
            vehicle.add_section_path(depot, self.graph[vehicle.position][depot]["weight"])

        self.final_objective = self.func_objective(self.solution, self.rho)
        return self.solution
            