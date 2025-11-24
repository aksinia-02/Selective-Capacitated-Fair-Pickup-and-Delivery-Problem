"""
This class contains general help functions used by the different neighborhood structures.
"""

def predict_new_path_length_after_intra_swap(vehicle, cust_a, cust_b):
    """
    This function returns the new path length of a vehicle, if the request pairs of two customers inside
    the same vehicle would be swapped. (pickup_a swapped with pickup_b and dropoff_a swapped with dropoff_b)
    The vehicle path is not changed.

    vehicle: is the vehicle object
    cust_a, cust_b: the customer objects whose points should be swapped.
    """

    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    length = vehicle.path_length

    path = vehicle.path

    first_visit = min([p_a, p_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == p_a:
        path, length = vehicle.predict_path_after_remove(p_a, path, length)
        path, length = vehicle.predict_path_after_replace(p_b, p_a, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, p_b, path, length)
    elif first_visit == p_b:
        path, length = vehicle.predict_path_after_remove(p_b, path, length)
        path, length = vehicle.predict_path_after_replace(p_a, p_b, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, p_a, path, length)

    first_visit = min([d_a, d_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == d_a:
        path, length = vehicle.predict_path_after_remove(d_a, path, length)
        path, length = vehicle.predict_path_after_replace(d_b, d_a, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, d_b, path, length)
    elif first_visit == d_b:
        path, length = vehicle.predict_path_after_remove(d_b, path, length)
        path, length = vehicle.predict_path_after_replace(d_a, d_b, path, length)
        path, length = vehicle.predict_path_after_add_after(pred, d_a, path, length)

    return length


def predict_new_path_length_after_intra_point_relocate(vehicle, point, pred):
    """
    This function returns the new path length of a vehicle, if one single point would be relocated inside the vehicle.
    (the point is moved right after pred)
    The vehicle path is not changed.

    vehicle: is the vehicle object
    point: the point to be relocated
    pred: the new predecessor of the point
    """

    length = vehicle.path_length
    path = vehicle.path

    path, length = vehicle.predict_path_after_remove(point, path, length)
    path, length = vehicle.predict_path_after_add_after(pred, point, path, length)

    return length


def predict_new_path_lengths_after_inter_swap(v1, v2, cust_a, cust_b):
    """
    This function returns the new path length of a vehicle, if the request pairs of two customers between
    two different vehicles would be swapped. (pickup_a swapped with pickup_b and dropoff_a swapped with dropoff_b)
    The vehicle paths are not changed.

    v1, v2: the vehicle objects
    cust_a, cust_b: the customer objects whose points should be swapped.
    """

    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    v1_path_length, v2_path_length = None, None

    if v1 is not None:
        v1_path_length = v1.path_length
        path = v1.path
        path, v1_path_length_1 = v1.predict_path_after_replace(p_a, p_b, path, v1_path_length)
        path, v1_path_length_2 = v1.predict_path_after_replace(d_a, d_b, path, v1_path_length)
        v1_path_length = v1_path_length_1 + v1_path_length_2 - v1.path_length
    if v2 is not None:
        v2_path_length = v2.path_length
        path = v2.path
        path, v2_path_length_1 = v2.predict_path_after_replace(p_b, p_a, path, v2_path_length)
        path, v2_path_length_2 = v2.predict_path_after_replace(d_b, d_a, path, v2_path_length)
        v2_path_length = v2_path_length_1 + v2_path_length_2 - v2.path_length

    return v1_path_length, v2_path_length


def predict_new_path_lengths_after_remove_and_append(vehicle, destination_vehicle, customer):
    """
    This function returns the new path length of two vehicles, if a request pair of a customer is removed from one
    vehicle and appended to another one.
    The vehicle paths are not changed.

    vehicle: the vehicle object from which the pickup and dropoff points are removed.
    destination_vehicle: the vehicle object which the pickup and dropoff points are appended to.
    customer: the customer object whose point should be removed and appended.
    """

    vehicle_path_length = vehicle.path_length
    path = vehicle.path
    path, vehicle_path_length = vehicle.predict_path_after_remove(customer.pickup, path, vehicle_path_length)
    path, vehicle_path_length = vehicle.predict_path_after_remove(customer.dropoff, path, vehicle_path_length)

    destination_vehicle_path_length = destination_vehicle.path_length
    path = destination_vehicle.path
    path, destination_vehicle_path_length = destination_vehicle.predict_path_after_add_after(path[-2], customer.pickup, path, destination_vehicle_path_length)
    path, destination_vehicle_path_length = destination_vehicle.predict_path_after_add_after(path[-2], customer.dropoff, path, destination_vehicle_path_length)

    return vehicle_path_length, destination_vehicle_path_length


def predict_new_path_lengths_after_move(vehicle, destination_vehicle, customer, pickup_pred, dropoff_pred):
    """
    This function returns the new path length of two vehicles, if a request pair of a customer is removed from one
    vehicle and inserted somewhere into another one.
    The vehicle paths are not changed.

    vehicle: the vehicle object from which the pickup and dropoff points are removed.
    destination_vehicle: the vehicle object which the pickup and dropoff points are inserted to.
    customer: the customer object whose point should be removed and appended.
    pickup_pred: the predecessor of the pickup point
    dropoff_pred: the predecessor of the dropoff point
    """

    vehicle_path_length = vehicle.path_length
    path = vehicle.path
    path, vehicle_path_length = vehicle.predict_path_after_remove(customer.pickup, path, vehicle_path_length)
    path, vehicle_path_length = vehicle.predict_path_after_remove(customer.dropoff, path, vehicle_path_length)

    destination_vehicle_path_length = destination_vehicle.path_length
    path = destination_vehicle.path
    path, destination_vehicle_path_length = destination_vehicle.predict_path_after_add_after(dropoff_pred, customer.dropoff, path, destination_vehicle_path_length)
    path, destination_vehicle_path_length = destination_vehicle.predict_path_after_add_after(pickup_pred, customer.pickup, path, destination_vehicle_path_length)

    return vehicle_path_length, destination_vehicle_path_length


def swap_pair_in_vehicle(vehicle, cust_a, cust_b):
    """
    This function swaps the request pairs of two customers inside the same vehicle.
    (pickup_a swapped with pickup_b and dropoff_a swapped with dropoff_b)

    vehicle: is the vehicle object
    cust_a, cust_b: the customer objects whose points should be swapped.
    """

    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    path = vehicle.path

    first_visit = min([p_a, p_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == p_a:
        vehicle.remove_section_path(p_a)
        vehicle.replace_point(p_b, p_a)
        vehicle.add_section_path_after(pred, p_b)
    elif first_visit == p_b:
        vehicle.remove_section_path(p_b)
        vehicle.replace_point(p_a, p_b)
        vehicle.add_section_path_after(pred, p_a)

    first_visit = min([d_a, d_b], key=lambda x: path.index(x))
    pred = path[path.index(first_visit) - 1]

    if first_visit == d_a:
        vehicle.remove_section_path(d_a)
        vehicle.replace_point(d_b, d_a)
        vehicle.add_section_path_after(pred, d_b)
    elif first_visit == d_b:
        vehicle.remove_section_path(d_b)
        vehicle.replace_point(d_a, d_b)
        vehicle.add_section_path_after(pred, d_a)


def swap_pairs_between_vehicles(v1, v2, cust_a, cust_b):
    """
    This function swaps the request pairs of two customers between two different vehicles.
    (pickup_a swapped with pickup_b and dropoff_a swapped with dropoff_b)

    v1, v2: the vehicle objects
    cust_a, cust_b: the customer objects whose points should be swapped.
    """

    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    if v1 is not None:
        v1.replace_point(p_a, p_b)
        v1.replace_point(d_a, d_b)
    if v2 is not None:
        v2.replace_point(p_b, p_a)
        v2.replace_point(d_b, d_a)


def relocate_point_in_vehicle(vehicle, point, pred):
    """
    This function relocates one single point inside the vehicle.
    (the point is moved right after pred)

    vehicle: is the vehicle object
    point: the point to be relocated
    pred: the new predecessor of the point
    """

    vehicle.remove_section_path(point)
    vehicle.add_section_path_after(pred, point)