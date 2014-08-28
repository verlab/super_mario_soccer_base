
import math


_cuts = lambda angle1: angle1 + 360 if angle1 < -180 else angle1
cut_angle = lambda angle1: angle1 - 360 if angle1 > 180 else _cuts(angle1)


def euclidean_distance(point1, point2):
    """
    Returns the Euclidean distance between two points on a plane.
    """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]

    return math.hypot(x2 - x1, y2 - y1)

def angle_between_points(point1, point2):
    """
    Returns the angle from the first point to the second, assuming that
    these points exist on a plane, and that the positive x-axis is 0 degrees
    and the positive y-axis is 90 degrees.  All returned angles are positive
    and relative to the positive x-axis.
    """
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    # get components of vector between the points
    dx = x2 - x1
    dy = y2 - y1

    # return the angle in degrees
    a = math.degrees(math.atan2(dy, dx))
    if a < 0:
        a += 360

    return a
