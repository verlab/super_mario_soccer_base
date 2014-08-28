import math
from smsoccer.util.geometric import angle_between_points


vDiff = lambda (bx, by), (ax, ay): (bx - ax, by - ay)
normV = lambda (x, y), n: (x / (1.0 * n), y / (1.0 * n))
Rot90R = lambda (x, y): (y, -x)


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

    v = (abs_coords[0] - b[0], abs_coords[1] - b[1])  #v =b - a
    theta = math.degrees(math.atan2(-v[0], v[1]))  #direction of v
    #theta = 180 + 180 / math.pi * math.atan2(v[0], v[1])
    #print "dir\t", f1.direction, "theta\t", theta, "\n"
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

    #print "number of flags", len(flags)

    if len(flags) < 2:
        return None

    # Take two flags
    f1, f2 = flags[:2]

    if f1.direction is None or f2.direction is None:
        print "Flag with direction None"
        return None

    if abs(f1.direction - f2.direction) == 180.0:
        #TODO Colinear 1
        return None
    elif f1.direction != f2.direction:
        # NonColinear
        return compute_non_colinear(f1, f2, flag_dict)
    elif f1.distance != f2.distance:
        # TODO Colinear
        return None
    else:
        return None