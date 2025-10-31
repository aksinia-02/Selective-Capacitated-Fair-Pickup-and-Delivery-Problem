import math

class Point:
    def __init__(self, x, y, index, type):
        self.x = x
        self.y = y
        self.index = index
        self.type = type

    def calculate_distance(self, a):
        """Compute Euclidean distance to another Point"""
        return math.sqrt((a.x - self.x)**2 + (a.y - self.y)**2)

    def __repr__(self):
        return f"(ind={self.index}, x={self.x}, y={self.y}, type={self.type})"