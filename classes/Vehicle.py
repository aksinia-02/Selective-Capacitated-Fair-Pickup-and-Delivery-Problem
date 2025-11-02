from classes.Point import Point
class Vehicle:

    fullfilled = 0 

    def __init__(self, index, capacity, position: Point):
        self.index = index
        self.capacity = capacity
        self.position = position
        self.load = 0
        self.path_length = 0
        self.path = {position.index}

    def __repr__(self):
        return f"Vehicle(capacity={self.capacity}, position={self.position})"
    
    def available_capacity(self):
        return self.capacity - self.load

    def add_section_path(self, other: Point):
        section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length
        self.path.add(other.index + 1)
        self.position = other