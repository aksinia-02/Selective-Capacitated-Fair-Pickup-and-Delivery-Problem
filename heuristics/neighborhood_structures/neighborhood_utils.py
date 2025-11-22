

def predict_new_path_length_after_intra_swap(vehicle, cust_a, cust_b):
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
    length = vehicle.path_length
    path = vehicle.path

    path, length = vehicle.predict_path_after_remove(point, path, length)
    path, length = vehicle.predict_path_after_add_after(pred, point, path, length)

    return length

def predict_new_path_lengths_after_inter_swap(v1, v2, cust_a, cust_b):
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

def swap_pair_in_vehicle(vehicle, cust_a, cust_b):
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
    p_a, d_a = cust_a.pickup, cust_a.dropoff
    p_b, d_b = cust_b.pickup, cust_b.dropoff

    if v1 is not None:
        v1.replace_point(p_a, p_b)
        v1.replace_point(d_a, d_b)
    if v2 is not None:
        v2.replace_point(p_b, p_a)
        v2.replace_point(d_b, d_a)

def relocate_point_in_vehicle(vehicle, point, pred):
    vehicle.remove_section_path(point)
    vehicle.add_section_path_after(pred, point)