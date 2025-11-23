from classes.Point import Point

class Customer:
    """
    Objects of this class contain information about a customer request.
    """

    def __init__(self, index, pickup: Point, dropoff: Point, goods):
        self.index = index
        self.pickup = pickup
        self.dropoff = dropoff
        self.goods = goods
        self.has_vehicle = False


    def __repr__(self):
        return f"Customer(ind={self.index}, pickup={self.pickup}, dropoff={self.dropoff}, goods={self.goods})"