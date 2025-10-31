from classes.Point import Point

class Customer:
    def __init__(self, pickup: Point, dropoff: Point, goods):
        self.pickup = pickup
        self.dropoff = dropoff
        self.goods = goods
        self.resp_vehicle = None

    def __repr__(self):
        return f"Customer(pickup={self.pickup}, dropoff={self.dropoff}, goods={self.goods})"

    def has_vehicle():
        return self.resp_vehicle is None