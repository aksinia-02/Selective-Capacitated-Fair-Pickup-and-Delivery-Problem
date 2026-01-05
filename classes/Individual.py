class Individual:
    __slots__ = ("solution", "fitness", "cost")

    def __init__(self, solution=None):
        self.solution = solution
        self.fitness = None
        self.cost = None
