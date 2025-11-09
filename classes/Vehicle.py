from classes.Point import Point
class Vehicle:

    def __init__(self, index, capacity, position: Point):
        self.index = index
        self.capacity = capacity
        self.position = position
        self.load = 0
        self.path_length = 0
        self.path = [position]
        self.load_history = [self.load]

    def __repr__(self):
        return f"Vehicle(index={self.index}, capacity={self.capacity}, load={self.load}, position={self.position}, path_length={self.path_length} path={self.path})"
    
    def available_capacity(self):
        return self.capacity - self.load

    def add_section_path(self, other: Point):
        section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length
        self.path.append(other)
        self.load += other.goods
        self.load_history.append(self.load)
        self.position = other
    
    def add_section_path_after(self, start: Point, new_location: Point):

        #start_index = self.path.index(start)
        start_index = next(i for i, p in enumerate(self.path) if p.index == start.index)
        if start_index == len(self.path) - 1:
            self.add_section_path(new_location)
        end = self.path[start_index + 1]
        self.path_length = self.path_length + start.calculate_distance(new_location) + new_location.calculate_distance(end) - start.calculate_distance(end)
        self.path.insert(start_index + 1, new_location)

        # update load history on path
        new_load = self.load_history[start_index] + new_location.goods
        self.load_history.insert(start_index + 1, new_load)
        for i in range(start_index + 2, len(self.load_history)):
            self.load_history[i] += new_location.goods

        # update load on current position
        current_index = self.path.index(self.position)
        if current_index >= start_index:
            self.load = self.load_history[current_index]

    def add_section_path_before(self, end: Point, new_location: Point):

        #end_index = self.path.index(end)
        end_index = next(i for i, p in enumerate(self.path) if p.index == end.index)
        start = self.path[end_index - 1]
        self.add_section_path_after(start, new_location)


    def remove_section_path(self, other: Point):
        #index = self.path.index(other)
        index = next(i for i, p in enumerate(self.path) if p.index == other.index)
        load_change = 0
        if 0 < index < len(self.path) - 1:
            start = self.path[index -1]
            end = self.path[index + 1]
            self.path_length = self.path_length + start.calculate_distance(end) - start.calculate_distance(other) - other.calculate_distance(end)

            load_change = self.load_history[index] - self.load_history[index - 1]
        elif index == len(self.path) - 1:
            start = self.path[index -1]
            self.path_length = self.path_length - start.calculate_distance(other)
            self.position = start

            load_change = self.load_history[index] - self.load_history[index - 1]
        elif index == 0:
            end = self.path[index + 1]
            self.path_length = self.path_length - other.calculate_distance(end)

            load_change = self.load_history[index]
        self.path.pop(index)
        self.load = self.load - load_change
        if index < len(self.load_history) - 1:
            for i in range(index + 1, len(self.load_history)):
                self.load_history[i] -= load_change
        self.load_history.pop(index)



    def replace_point(self, to_replace: Point, new_location: Point):
        self.add_section_path_after(to_replace, new_location)
        self.remove_section_path(to_replace)



    def replace_vehicle(self, new_vehicle):
        if not isinstance(new_vehicle, type(self)):
            raise TypeError(f"Expected a {type(self).__name__} object, got {type(new_vehicle).__name__}")

        self.index = new_vehicle.index
        self.capacity = new_vehicle.capacity
        self.position = new_vehicle.position
        self.load = new_vehicle.load
        self.path_length = new_vehicle.path_length
        self.path = new_vehicle.path
        self.load_history = new_vehicle.load_history

    def get_available_capacity_at_position_x(self, x: Point):

        start_index = self.path.index(x)
        load = 0
        for pos in self.path:
            if pos.type == 2:
                load += pos.goods
        return self.capacity - load

    def get_location_before_x(self, x: Point):
        index = self.path.index(x)
        return self.path[index - 1]

    def get_location_after_x(self, x: Point):
        index = self.path.index(x)
        return self.path[index + 1]
