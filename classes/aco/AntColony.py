from classes.aco.Ant import Ant

class AntColony:

    def __init__(self, graph, alpha, beta, initial_solution, func_objective):
        Ant.init_static_class_variables(graph, (len(graph.nodes()) - 1) // 2, alpha, beta)
        self.n_vehicles = len(initial_solution)
        self.ants = self.create_ants(initial_solution, graph)
        self.solution = initial_solution
        self.func_objective = func_objective

    def create_ants(self, vehicles, graph):
        n_ants = len(vehicles)

        ants = []
        for i in range(n_ants):
            ants.append(Ant(i, 0.2, position=vehicles[0].path[0], capacity=vehicles[0].capacity, vehicle=vehicles[i]))
        return ants
    
    def construct_solution(self):
        active_ants_counter = self.n_vehicles

        while active_ants_counter > 0:
            best_obj = 0
            best_next = None
            best_ant = 0
            for i, ant in enumerate(self.ants):
                if ant.active:
                    print(f"start ant: {i}")
                    next_node_ind, weight = ant.get_next_step()
                    ant.vehicle.path_length += weight
                    print(f"node {next_node_ind} with weight {weight} is selected")
                    objective = self.func_objective(self.solution)
                    print(objective)
                    if self.func_objective(self.solution) > best_obj:
                        best_obj = objective
                        best_next = next_node_ind
                        best_ant = i
                        print(f"new best ant: {best_ant}")
                    ant.vehicle.path_length -= weight
            for i, ant in enumerate(self.ants):
                if i == best_ant:
                    completed_path = ant.make_step()
                else:
                    completed_path = ant.delete_assigned_node(best_next)
                if completed_path:
                    active_ants_counter -= 1
                    ant.active = False

        # for vehicle in self.solution:
        #     vehicle.add
            