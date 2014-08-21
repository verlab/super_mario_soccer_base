from smsoccer.util.geometric import euclidean_distance, angle_between_points


class Actuator(object):

    def __init__(self, world_model):
        self.wm = world_model


    def kick_to(self, point, extra_power=0.0):
        """
        Kick the ball to some point with some extra-power factor added on.
        extra_power=0.0 means the ball should stop at the given point, anything
        higher means it should have proportionately more speed.
        """

        # how far are we from the desired point?
        point_dist = euclidean_distance(self.wm.abs_coords, point)

        # get absolute direction to the point
        abs_point_dir = angle_between_points(self.wm.abs_coords, point)

        # get relative direction to point from body, since kicks are relative to
        # body direction.
        if self.wm.abs_body_dir is not None:
            rel_point_dir = self.wm.abs_body_dir - abs_point_dir

        # we do a simple linear interpolation to calculate final kick speed,
        # assuming a kick of power 100 goes 45 units in the given direction.
        # these numbers were obtained from section 4.5.3 of the documentation.
        # TODO: this will fail if parameters change, needs to be more flexible
        max_kick_dist = 45.0
        dist_ratio = point_dist / max_kick_dist

        # find the required power given ideal conditions, then add scale up by
        # difference between actual aceivable power and maximum power.
        required_power = dist_ratio * self.wm.server_parameters.maxpower
        effective_power = self.wm.get_effective_kick_power(self.wm.ball,
                                                        required_power)
        required_power += 1 - (effective_power / required_power)

        # add more power!
        power_mod = 1.0 + extra_power
        power = required_power * power_mod

        # do the kick, finally
        self.wm.ah.kick(rel_point_dir, power)


    #todo Actuator
    def turn_neck_to_object(self, obj):
        """
        Turns the player's neck to a given object.
        """

        self.wm.ah.turn_neck(obj.direction)


    #todo Actuator
    def turn_body_to_point(self, point):
        """
        Turns the agent's body to face a given point on the field.
        """

        # calculate absolute direction to point
        abs_point_dir = angle_between_points(self.wm.abs_coords, point)

        # subtract from absolute body direction to get relative angle
        relative_dir = self.wm.abs_body_dir - abs_point_dir

        # turn to that angle
        self.wm.ah.turn(relative_dir)


    #todo Actuator
    def teleport_to_point(self, point):
        """
        Teleport the player to a given (x, y) point using the 'move' command.
        """

        self.wm.ah.move(point[0], point[1])

    #todo Actuator
    def align_neck_with_body(self):
        """
        Turns the player's neck to be in line with its body, making the angle
        between the two 0 degrees.
        """

        # neck angle is relative to body, so we turn it back the inverse way
        if self.wm.neck_direction is not None:
            self.wm.ah.turn_neck(self.wm.neck_direction * -1)

    def turn_body_to_object(self, obj):
        """
        Turns the player's body to face a particular object.
        """

        self.wm.ah.turn(obj.direction)