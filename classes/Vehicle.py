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
    
    def copy(self):
        copy_vehicle = Vehicle(self.index, self.capacity, self.position)
        copy_vehicle.load = self.load
        copy_vehicle.path_length = self.path_length
        copy_vehicle.path = self.path
        copy_vehicle.load_history = self.load_history
        return copy_vehicle


    
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
        start_index = next(i for i, p in enumerate(self.path) if p == start)
        if start_index == len(self.path) - 1:
            self.add_section_path(new_location)
        else:
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
        end_index = next(i for i, p in enumerate(self.path) if p == end)
        start = self.path[end_index - 1]
        self.add_section_path_after(start, new_location)


    def remove_section_path(self, other: Point):
        #index = self.path.index(other)
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
        if index < len(self.load_history) - 1:
            for i in range(index + 1, len(self.load_history)):
                self.load_history[i] -= load_change
        self.load_history.pop(index)

    def predict_path_after_remove(self, other: Point, path=None, path_length=None):
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

