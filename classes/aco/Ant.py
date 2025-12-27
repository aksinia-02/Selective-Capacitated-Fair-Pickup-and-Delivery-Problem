from classes.Point import Point
import random

class Ant:

    graph = None
    n_customers = 0
    alpha = 0
    beta = 0

    def __init__(self, index, scent_strength, position: Point, capacity):
        self.index = index
        self.scent_strength = scent_strength
        # start from depot
        self.position = position
        self.capacity = capacity
        self.load = 0
        self.color = (random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
        self.visited = {}

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
        self.load += next_node.goods
        if self.position.index != 0:
            self.visited[self.position.index] = self.position

    def get_feasible_neighbors(self):
        feasible = []

        for n in self.graph.neighbors(self.position):
            if self._pickup_delivery(n) and self._enough_capacity(n):
                feasible.append(n)

        return feasible
    
    def _pickup_delivery(self, n: Point):
        index = n.index

        if index in self.visited:
            return False
        
        if index <= self.n_customers:
            return True
        
        pickup_ind = index - self.n_customers
        return pickup_ind in self.visited
    
    def _enough_capacity(self, n: Point):
        return self.capacity >= n.goods + self.load
    
    def compute_transition_probabilities(self, feasible_nodes):
        weights = []

        for j in feasible_nodes:
            tau = self.graph[self.position][j]["scent"]
            eta = 1 / self.graph[self.position][j]["weight"]

            value = (tau ** self.alpha) * (eta ** self.beta)
            weights.append(value)

        total = sum(weights)

        probabilities = [w / total for w in weights]
        return probabilities
    
    def __repr__(self):
        return f"(ind={self.index}, scent_strength={self.scent_strength}, position={self.position}, load={self.load})"
