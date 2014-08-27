import math


vDiff = lambda (bx, by), (ax, ay): (bx - ax, by - ay)
normV = lambda (x, y), n: (x / (1.0 * n), y / (1.0 * n))
Rot90R = lambda (x, y): (y, -x)


def compute_colinear(f1, f2, flag_dict, mid=1):
    if f1.distance > f2.distance:
        f1, f2 = f2, f1

    da, db = f1.distance, f2.distance
    # Real position of the flags
    rf1 = flag_dict[f1.flag_id]
    rf2 = flag_dict[f2.flag_id]

    b_a = vDiff(rf2, rf1)  # difference vector

    lb_a = math.hypot(*b_a)
    nb_a = normV(b_a, lb_a)

    va = (mid * nb_a[0] * da, mid * nb_a[1] * da)
    vb = (nb_a[0] * db, nb_a[1] * db)
    ea = (rf1[0] + va[0], rf1[1] + va[1])
    eb = (rf2[0] + vb[0], rf2[1] + vb[1])
    return (ea[0] + eb[0]) / 2.0, (ea[1] + eb[1]) / 2.0


def compute_non_colinear(f1, f2, flag_dict):
    """
    Compute robot localization based on two flags.
    :param f1: flag 1
    :param f2: flag 2
    :param flag_dict: dictionary of flags and real positions.
    :return:
    """
    # Order flags
    if f1.direction < f2.direction:
        f1, f2 = f2, f1

    # Real position of the flags
    rf1 = flag_dict[f1.flag_id]
    rf2 = flag_dict[f2.flag_id]

    b_a = vDiff(rf2, rf1)  # difference vector
    lb_a = math.hypot(*b_a)  # norm of difference
    nb_a = normV(b_a, lb_a)  # normalized difference
    rndiff = Rot90R(nb_a)  # normalized -90o rotation
    lpcomp = (lb_a ** 2 + f1.distance ** 2 - f2.distance ** 2) / (2 * lb_a)  # norm of parallel component

    try:
        lrcomp = (f1.distance ** 2 - lpcomp ** 2) ** 0.5  # norm of rotated component
    except:
        return None

    pcomp = (lpcomp * nb_a[0], lpcomp * nb_a[1])  # parallel component
    rcomp = (lrcomp * rndiff[0], lrcomp * rndiff[1])  # rotated component
    # return the location
    return rf1[0] + pcomp[0] + rcomp[0], rf1[1] + pcomp[1] + rcomp[1]


def triangulate_direction(abs_coords, flags, flag_dict):
    """
    Determines absolute view angle for the player given a list of visible
    flags.  We find the absolute angle to each flag, then return the average
    of those angles.  Returns 'None' if no angle could be determined.
    :param abs_coords: position of the robot
    """
    f1 = None
    for f in flags:
        if f.distance is None or f.direction is None:
            continue

        if f1 is None:
            f1 = f
            continue

        if f.distance < f1.distance:
            # f2 = f1
            f1 = f

    b = flag_dict[f1.flag_id]

    v = (b[0] - abs_coords[0], b[1] - abs_coords[1])  #v =b - a
    theta = math.degrees(math.atan2(v[1], v[0]))  #direction of v
    dir = - f1.direction + theta

    return dir


def triangulate_position(flags, flag_dict):
    """
    Returns a best-guess position based on the triangulation via distances
    to all flags in the flag list given.  'angle_step' specifies the
    increments between angles for projecting points onto the circle
    surrounding a flag.
    :param flags: observed flags
    :param flag_dict: real positions for flags
    """

    if len(flags) < 2:
        return None

    # Take two flags
    f1, f2 = flags[:2]

    if f1.distance is None or f1.direction is None or f1.flag_id is None:
        return triangulate_position(flags[1:], flag_dict)

    if f2.distance is None or f2.direction is None or f2.flag_id is None:
        flags2 = flags[:]
        flags2.remove(f2)
        return triangulate_position(flags2, flag_dict)

    if f1.direction is None or f2.direction is None:
        print "Flag with direction None"
        return None

    if abs(f1.direction - f2.direction) == 180.0:
        return compute_colinear(f1, f2, flag_dict, -1)

    elif f1.direction != f2.direction:
        # NonColinear
        return compute_non_colinear(f1, f2, flag_dict)

    elif f1.distance != f2.distance:
        return compute_colinear(f1, f2, flag_dict)
    else:
        return None