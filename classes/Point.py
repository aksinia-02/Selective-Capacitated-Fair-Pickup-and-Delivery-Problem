import math

class Point:
    def __init__(self, x, y, index, type, goods):
        self.x = x
        self.y = y
        self.index = index
        self.type = type
        self.goods = goods

    def calculate_distance(self, a):
        """Compute Euclidean distance to another Point"""
        return math.ceil(math.sqrt((a.x - self.x)**2 + (a.y - self.y)**2))

    def __repr__(self):
        return f"(ind={self.index}, x={self.x}, y={self.y}, type={self.type}, goods={self.goods})"

    def __eq__(self, other):
        return self.index == other.index and self.x == other.x and self.y == other.y and self.type == other.type and self.goods == other.goods

    def __hash__(self):
        return hash((self.index, self.x, self.y, self.type, self.goods))