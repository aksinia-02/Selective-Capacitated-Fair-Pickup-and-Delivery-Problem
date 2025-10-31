from classes.Point import Point
class Vehicle:

    fullfilled = 0 

    def __init__(self, capacity, position: Point):
        self.capacity = capacity
        self.position = position
        self.weight = 0
        self.path_length = 0

    def __repr__(self):
        return f"Vehicle(capacity={self.capacity}, position={self.position})"
    
    def available_capacity(self):
        return self.capacity - self.weight

    def add_section_path(self, other: Point):
        section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length