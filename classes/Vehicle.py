from classes.Point import Point

class Vehicle:
    """
    Objects of this class represent vehicles. All vehicles together represent a solution for the problem.
    """

    def __init__(self, index, capacity, position: Point):
        """
        This function defines a Vehicle object.

        index: a unique identifier for the vehicle.
        capacity: capacity of the vehicle.
        position: current position of the vehicle.
        load: load of the vehicle at position.
        path_length: total path length of the vehicle computed by the euclidean distance.
        path: list of points (typically starts and ends with a type 1 point and has other points in between).
        load_history: history of load of the vehicle (for each point of the path the current load).
        """

        self.index = index
        self.capacity = capacity
        self.position = position
        self.load = 0
        self.path_length = 0
        self.path = [position]
        self.load_history = [self.load]


    def __repr__(self):
        return f"Vehicle(index={self.index}, capacity={self.capacity}, load={self.load}, position={self.position}, path_length={self.path_length} path={self.path})"
    
    def print_path(self):
        result_string = ""
        for n in self.path:
            result_string += f"{n.index}, "
        return result_string


    def copy(self):
        """
        This function returns a copy of the Vehicle object.
        """

        copy_vehicle = Vehicle(self.index, self.capacity, self.position)
        copy_vehicle.load = self.load
        copy_vehicle.path_length = self.path_length
        copy_vehicle.path = self.path
        copy_vehicle.load_history = self.load_history
        return copy_vehicle


    def available_capacity(self):
        """
        This function returns the current available capacity of the Vehicle object.
        """

        return self.capacity - self.load


    def add_section_path(self, other: Point, section_length=None):
        """
        This function adds a new point at the end of the path of this vehicle.
        The path, path_length, load, load_history and position are updated accordingly.

        other: the new point to be added.
        """
        if not section_length:
            section_length = self.position.calculate_distance(other)
        self.path_length  = self.path_length + section_length
        self.path.append(other)
        self.load += other.goods
        self.load_history.append(self.load)
        self.position = other


    def add_section_path_after(self, start: Point, new_location: Point):
        """
        This function adds a new point right after another point of the path of this vehicle.
        The path, path_length, load, load_history and position are updated accordingly.

        start: the point after which to add the new point.
        new_location: the new point to be added.
        """

        start_index = next(i for i, p in enumerate(self.path) if p == start)
        if start_index == len(self.path) - 1:
            self.add_section_path(new_location)
        else:
            end = self.path[start_index + 1]
            self.path_length = self.path_length + start.calculate_distance(new_location) + new_location.calculate_distance(end) - start.calculate_distance(end)
            self.path.insert(start_index + 1, new_location)

            # update load history on path
            load = 0
            self.load_history = []
            for p in self.path:
                load += p.goods
                self.load_history.append(load)

            # update load on current position
            current_index = self.path.index(self.position)
            if current_index >= start_index:
                self.load = self.load_history[current_index]


    def add_section_path_before(self, end: Point, new_location: Point):
        """
        This function adds a new point right before another point of the path of this vehicle.
        The path, path_length, load, load_history and position are updated accordingly.

        end: the point before which to add the new point.
        new_location: the new point to be added.
        """

        end_index = next(i for i, p in enumerate(self.path) if p == end)
        start = self.path[end_index - 1]
        self.add_section_path_after(start, new_location)


    def remove_section_path(self, other: Point):
        """
        This function removes a point from the path of this vehicle.
        The path, path_length, load, load_history and position are updated accordingly.

        other: the point to be removed.
        """

        index = next(i for i, p in enumerate(self.path) if p == other)
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

        load = 0
        self.load_history = []
        for p in self.path:
            load += p.goods
            self.load_history.append(load)



    def predict_path_after_remove(self, other: Point, path=None, path_length=None):
        """
        This function returns the path and the length of the path that would be the result of removing a point
        from the path.
        This function does not change this object.

        other: the point to be removed.
        path: the path where the point should be removed from (if None, the path of this vehicle will be used for computation).
        path_length: the length of the path where the point should be removed from.
        """

        if path is None:
            path = self.path
        if path_length is None:
            path_length = self.path_length
        index = next(i for i, p in enumerate(path) if p == other)
        new_path = path.copy()
        new_path.pop(index)

        if 0 < index < len(path) - 1:
            start = path[index - 1]
            end = path[index + 1]
            path_length = path_length + start.calculate_distance(end) - start.calculate_distance(other) - other.calculate_distance(end)

        elif index == len(path) - 1:
            start = path[index - 1]
            path_length = path_length - start.calculate_distance(other)

        elif index == 0:
            end = path[index + 1]
            path_length = path_length - other.calculate_distance(end)

        return new_path, path_length


    def predict_path_after_add_after(self, start: Point, new_location: Point, path=None, path_length=None):
        """
        This function returns the path and the length of the path that would be the result of adding a point
        to the path right after the point start.
        This function does not change this object.

        start: the point after which to add the new point.
        new_location: the new point to be added.
        path: the path where the point should be added to (if None, the path of this vehicle will be used for computation).
        path_length: the length of the path where the point should be added to.
        """

        if path is None:
            path = self.path
        if path_length is None:
            path_length = self.path_length
        start_index = next(i for i, p in enumerate(path) if p == start)
        new_path = path.copy()
        new_path.insert(start_index + 1, new_location)

        if start_index == len(path) - 1:
            section_length = self.position.calculate_distance(new_location)
            return path_length + section_length
        end = path[start_index + 1]

        return new_path, path_length + start.calculate_distance(new_location) + new_location.calculate_distance(end) - start.calculate_distance(end)


    def predict_path_after_replace(self, to_replace: Point, new_location: Point, path=None, path_length=None):
        """
        This function returns the path and the length of the path that would be the result of replacing a point
        with another one in the path.
        This function does not change this object.

        to_replace: the point to be replaced.
        new_location: the new point to replace the other one with.
        path: the path where the point should be replaced (if None, the path of this vehicle will be used for computation).
        path_length: the length of the path where the point should be replaced.
        """

        if path is None:
            path = self.path
        if path_length is None:
            path_length = self.path_length
        index = next(i for i, p in enumerate(path) if p == to_replace)
        new_path = path.copy()
        new_path.pop(index)
        new_path.insert(index, new_location)

        if 0 < index < len(path) - 1:
            start = path[index - 1]
            end = path[index + 1]
            path_length = path_length + start.calculate_distance(new_location) + new_location.calculate_distance(end) - start.calculate_distance(to_replace) - to_replace.calculate_distance(end)

        elif index == len(path) - 1:
            start = path[index - 1]
            path_length = path_length - start.calculate_distance(to_replace) + start.calculate_distance(new_location)

        elif index == 0:
            end = path[index + 1]
            path_length = path_length - to_replace.calculate_distance(end) + new_location.calculate_distance(end)

        return new_path, path_length


    def replace_point(self, to_replace: Point, new_location: Point):
        """
        This function replaces a point in the path of this vehicle by another point.
        The path, path_length, load, load_history and position are updated accordingly.

        to_replace: the point to be replaced.
        new_location: the new point to replace the other one with.
        """

        self.add_section_path_after(to_replace, new_location)
        self.remove_section_path(to_replace)



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
    
    def simple_remove_point(self, point: Point):

        index = next(i for i, p in enumerate(self.path) if p == point)
        after = self.path[index+1]
        before = self.path[index-1]
        self.path_length = self.path_length - point.calculate_distance(before) - point.calculate_distance(after) + before.calculate_distance(after)
        self.path.remove(point)

    def simple_add_point_after(self, before: Point, point: Point):

        start_index = next(i for i, p in enumerate(self.path) if p == before)
        end = self.path[start_index + 1]
        self.path_length = self.path_length + point.calculate_distance(before) + point.calculate_distance(end) - before.calculate_distance(end)
        self.path.insert(start_index + 1, point)

    def calculate_path_length(self):
        result = 0
        for i in range(len(self.path)-1):
            result += self.path[i].calculate_distance(self.path[i+1])
        return result

