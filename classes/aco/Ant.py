from classes.Point import Point
import random

class Ant:

    graph = None
    n_customers = alpha = beta = 0
    pickups = {}
    dropoffs = {}
    depot = None

    def __init__(self, index, scent_strength, position: Point, capacity):
        self.index = index
        self.scent_strength = scent_strength
        # start from depot
        self.position = position
        self.capacity = capacity
        self.load = 0
        self.color = (random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
        self.pos_next_nodes = self.pickups

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

    def construct_soltution(self, vehicles):
        while self.pos_next_nodes:
            self.make_step()



    def make_step(self):
        neighbors = self.get_feasible_neighbors()
        probs = self.compute_transition_probabilities(neighbors)
        next_node = random.choices(neighbors, weights=probs, k=1)[0]
        self.graph[self.position][next_node]["scent"] += self.scent_strength
        old_color = self.graph[self.position][next_node]["color"]
        self.graph[self.position][next_node]["color"] = (
            (old_color[0] + self.color[0]) // 2,
            (old_color[1] + self.color[1]) // 2,
            (old_color[2] + self.color[2]) // 2
        )
        self.position = next_node
        print(f"new position: {self.position}")
        self.load += next_node.goods

        result_string = ""
        for _, n in self.pos_next_nodes.items():
            result_string += f"{n.index}, "
        print(result_string)

        if self.position.index != 0:
            #self.pos_next_nodes[0] = self.depot
            print(f"add: {0}")
            if next_node.index <= self.n_customers:
                d_index = self.n_customers + next_node.index
                print(f"add: {d_index}")
                self.pos_next_nodes[d_index] = self.dropoffs[d_index]
        self.pos_next_nodes.pop(next_node.index)
        print(f"delete: {next_node.index}")


    def get_feasible_neighbors(self):
        feasible = []

        for _, n in self.pos_next_nodes.items():
            if self.capacity >= n.goods + self.load:
                feasible.append(n)

        return feasible
    
    # def _pickup_delivery(self, n: Point):
    #     index = n.index

    #     if index in self.visited:
    #         return False
        
    #     if index <= self.n_customers:
    #         return True
        
    #     pickup_ind = index - self.n_customers
    #     return pickup_ind in self.visited
    
    def _enough_capacity(self, n: Point):
        return self.capacity >= n.goods + self.load
    
    def compute_transition_probabilities(self, feasible_nodes):
        weights = []

        for j in feasible_nodes:
            tau = self.graph[self.position][j]["scent"]
            eta = 1 / max(self.graph[self.position][j]["weight"], 1e-6)

            value = (tau ** self.alpha) * (eta ** self.beta)
            weights.append(value)

        total = sum(weights)

        probabilities = [w / total for w in weights]
        return probabilities
    
    def __repr__(self):
        return f"(ind={self.index}, scent_strength={self.scent_strength}, position={self.position}, load={self.load})"
