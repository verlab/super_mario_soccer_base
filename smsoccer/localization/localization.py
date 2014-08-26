import math
from smsoccer.util.geometric import euclidean_distance, angle_between_points


vDiff = lambda (bx, by), (ax, ay): (bx - ax, by - ay)
normV = lambda (x, y), n: (x / (1.0 * n), y / (1.0 * n))
Rot90R = lambda (x, y): (y, -x)


def compute_non_colinear(f1, f2, flag_dict):
    if f1.direction < f2.direction:
        f1, f2 = f2, f1

    # da, db = objects[0].get('distance'), objects[1].get('distance')

    a = flag_dict[f1.flag_id]
    b = flag_dict[f2.flag_id]

    b_a = vDiff(b, a)  # difference vector
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
    return a[0] + pcomp[0] + rcomp[0], a[1] + pcomp[1] + rcomp[1]


def triangulate_direction(abs_coords, flags, flag_dict):
    """
    Determines absolute view angle for the player given a list of visible
    flags.  We find the absolute angle to each flag, then return the average
    of those angles.  Returns 'None' if no angle could be determined.
    """
    # average all flag angles together and save that as absolute angle
    abs_angles = []
    for f in flags:
        # if the flag has useful data, consider it
        if f.distance is not None and f.flag_id in flag_dict:
            flag_point = flag_dict[f.flag_id]
            abs_dir = angle_between_points(abs_coords, flag_point)
            abs_angles.append(abs_dir)

    # return the average if available
    if len(abs_angles) > 0:
        return sum(abs_angles) / len(abs_angles)

    return None

def triangulate_position(flags, flag_dict):
    """
    Returns a best-guess position based on the triangulation via distances
    to all flags in the flag list given.  'angle_step' specifies the
    increments between angles for projecting points onto the circle
    surrounding a flag.
    """

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