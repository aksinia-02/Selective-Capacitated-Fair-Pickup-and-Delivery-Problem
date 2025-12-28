from classes.Point import Point
import random
import copy

class Ant:

    graph = None
    n_customers = alpha = beta = 0
    pickups = {}
    dropoffs = {}
    depot = None

    def __init__(self, index, scent_strength, vehicle):
        self.index = index
        self.scent_strength = scent_strength
        self.vehicle = vehicle
        self.color = (random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
        self.pos_next_nodes = copy.deepcopy(self.pickups)
        self.next_node = None
        self.active = True

    @classmethod
    def init_static_class_variables(cls, graph, n_customers, alpha, beta):

        cls.graph = graph
        cls.n_customers = n_customers
        cls.alpha = alpha
        cls.beta = beta
        for n in cls.graph.nodes():
            n_ind = n.index
            type = n.type
            if type == 1:
                cls.depot = n
            elif type == 2:
                cls.pickups[n_ind] = n
            else:
                cls.dropoffs[n_ind] = n

    def delete_assigned_node(self, node: Point):
        if self.active:
            if self.next_node.index == node.index:
                self.next_node = None
            self.pos_next_nodes.pop(node.index, None)
        return len(self.pos_next_nodes) == 0

    def get_next_step(self):
        if not self.next_node:
            neighbors = self.get_feasible_neighbors()
            probs = self.compute_transition_probabilities(neighbors)
            next_node = random.choices(neighbors, weights=probs, k=1)[0]
            self.next_node = next_node
        else:
            next_node = self.next_node
        return next_node, self.graph[self.vehicle.position][next_node]["weight"]


    def make_step(self):
        # self.graph[self.vehicle.position][self.next_node]["scent"] += self.scent_strength
        # self.graph[self.vehicle.position][self.next_node]["color"] = self.color

        self.vehicle.add_section_path(self.next_node, self.graph[self.vehicle.position][self.next_node]["weight"])

        if self.next_node.index <= self.n_customers:
            d_index = self.n_customers + self.next_node.index
            self.pos_next_nodes[d_index] = self.dropoffs[d_index]
        self.pos_next_nodes.pop(self.next_node.index)
        self.next_node = None

        return len(self.pos_next_nodes) == 0


    def get_feasible_neighbors(self):
        feasible = []
        # result_string = ""
        # for _, n in self.pos_next_nodes.items():
        #     result_string += f"{n.index}, "
        # print(result_string)

        for _, n in self.pos_next_nodes.items():
            if self.vehicle.capacity >= n.goods + self.vehicle.load:
                feasible.append(n)

        return feasible
    
    def compute_transition_probabilities(self, feasible_nodes):
        weights = []

        for j in feasible_nodes:
            tau = self.graph[self.vehicle.position][j]["scent"]
            eta = 1 / max(self.graph[self.vehicle.position][j]["weight"], 1e-6)

            value = (tau ** self.alpha) * (eta ** self.beta)
            weights.append(value)

        total = sum(weights)

        probabilities = [w / total for w in weights]
        return probabilities
    
    def __repr__(self):
        return f"(ind={self.index}, scent_strength={self.scent_strength}, vehicle_path={self.vehicle.path}"
