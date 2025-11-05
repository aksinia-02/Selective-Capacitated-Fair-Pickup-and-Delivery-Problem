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
        self.load_history = [self.load]

    def __repr__(self):
        return f"Vehicle(capacity={self.capacity}, position={self.position})"
    
    def available_capacity(self):
        return self.capacity - self.load

    def add_section_path(self, other: Point, load_change=0):
        section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length
        self.path.append(other)
        self.load += load_change
        self.load_history.append(self.load)
        self.position = other
    
    def add_section_path_between(self, start: Point, new_location: Point, load_change=0):

        start_index = self.path.index(start)
        end = self.path[start_index + 1]
        self.path_length  = start.calculate_distance(new_location) + end.calculate_distance(new_location) - start.calculate_distance(end)
        self.path.insert(start_index + 1, new_location)

        # update load history on path
        new_load = self.load_history[start_index] + load_change
        self.load_history.insert(start_index + 1, new_load)
        for i in range(start_index + 2, len(self.load_history)):
            self.load_history[i] += load_change

        # update load on current position
        current_index = self.path.index(self.position)
        if current_index >= start_index:
            self.load = self.load_history[current_index]


    def replace(self, new_vehicle):
        if not isinstance(new_vehicle, type(self)):
            raise TypeError(f"Expected a {type(self).__name__} object, got {type(new_vehicle).__name__}")

        self.index = new_vehicle.index
        self.capacity = new_vehicle.capacity
        self.position = new_vehicle.position
        self.load = new_vehicle.load
        self.path_length = new_vehicle.path_length
        self.path = new_vehicle.path
        self.load_history = new_vehicle.load_history
