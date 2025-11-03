from classes.Point import Point
class Vehicle:

    fullfilled = 0 

    def __init__(self, index, capacity, position: Point):
        self.index = index
        self.capacity = capacity
        self.position = position
        self.load = 0
        self.path_length = 0
        self.path = [position]

    def __repr__(self):
        return f"Vehicle(capacity={self.capacity}, position={self.position})"
    
    def available_capacity(self):
        return self.capacity - self.load

    def add_section_path(self, other: Point):
        section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length
        self.path.append(other)
        self.position = other
    
    def add_section_path_between(self, start: Point, new_location: Point):

        start_index = self.path.index(start)
        end = self.path[start_index + 1]
        self.path_length  = start.calculate_distance(new_location) + end.calculate_distance(new_location) - start.calculate_distance(end)
        self.path.insert(start_index + 1, new_location)