import math

class Point:
    """
    This class represents a Point object.
    """

    def __init__(self, x, y, index, type, goods):
        """
        This function defines a Point object.

        x, y: the coordinates of the point.
        index: a unique identifier for the point.
        type: the type of point. (1 is the depot, 2 is a pickup point and 3 is a dropoff point)
        goods: if the point is a pickup point, this is the amount of goods. If the point is a dropoff,
                this is the negative amount of goods.
        """

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