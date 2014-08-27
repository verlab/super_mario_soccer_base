from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.util.geometric import euclidean_distance, angle_between_points
from smsoccer.world.world_model import PlayModes, WorldModel

class AbstractPlayer(AbstractAgent):
    """
    AbstractPlayer class

    Has function to help any kind of agent
    """

    def __init__(self, goalie = False):
        super(AbstractPlayer, self).__init__( goalie = goalie )

    def teleport_to_point(self, point):
        """
        Teleport the player to a given (x, y) point using the 'move' command.
        """
        self.wm.ah.move(point[0], point[1])

    def align_neck_with_body(self):
        """
        Turns the player's neck to be in line with its body, making the angle
        between the two 0 degrees.
        """
        # neck angle is relative to body, so we turn it back the inverse way
        if self.wm.neck_direction is not None:
            self.wm.ah.turn_neck(self.neck_direction * -1)

    def get_nearest_teammate_to_point(self, point):
        """
        Returns the uniform number of the fastest teammate to some point.
        """

        # holds tuples of (player dist to point, player)
        distances = []
        for p in self.wm.players:
            # skip enemy and unknown players
            if self.wm.p.side != self.wm.side:
                continue

            # find their absolute position
            p_coords = self.wm.get_object_absolute_coords(p)

            distances.append((euclidean_distance(point, p_coords), p))

        # return the nearest known teammate to the given point
        nearest = min(distances)[1]
        return nearest

    def get_stamina(self):
        """
        Returns the agent's current stamina amount.
        """
        return self.wm.stamina

    def turn_body_to_object(self, obj):
        """
        Turns the player's body to face a particular object.
        """
        self.wm.ah.turn(obj.direction)


    def turn_neck_to_object(self, obj):
        """
        Turns the player's neck to a given object.
        """
        self.wm.ah.turn_neck(obj.direction)


    def get_distance_to_point(self, point):
        """
        Returns the linear distance to some point on the field from the current
        point.
        """
        return euclidean_distance(self.wm.abs_coords, point)

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

    def get_effective_kick_power(self, ball, power):
        """
        Returns the effective power of a kick given a ball object.  See formula
        4.21 in the documentation for more details.
        """

        # we can't calculate if we don't have a distance to the ball
        if ball.distance is None:
            return

        # first we get effective kick power:
        # limit kick_power to be between minpower and maxpower
        kick_power = max(min(power, self.wm.server_parameters.maxpower),
                         self.wm.server_parameters.minpower)

        # scale it by the kick_power rate
        kick_power *= self.wm.server_parameters.kick_power_rate

        # now we calculate the real effective power...
        a = 0.25 * (ball.direction / 180)
        b = 0.25 * (ball.distance / self.wm.server_parameters.kickable_margin)

        # ...and then return it
        return 1 - a - b

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
        # difference between actual achievable power and maximum power.
        required_power = dist_ratio * self.wm.server_parameters.maxpower
        effective_power = self.get_effective_kick_power(self.wm.ball, required_power)
        required_power += 1 - (effective_power / required_power)

        # add more power!
        power_mod = 1.0 + extra_power
        power = required_power * power_mod

        # do the kick, finally
        self.wm.ah.kick(power, rel_point_dir)


    def is_dead_ball_them(self):
        """
        Returns whether the ball is in the other team's possession and it's a
        free kick, corner kick, or kick in.
        """

        # shorthand for verbose constants
        kil = PlayModes.KICK_IN_L
        kir = PlayModes.KICK_IN_R
        fkl = PlayModes.FREE_KICK_L
        fkr = PlayModes.FREE_KICK_R
        ckl = PlayModes.CORNER_KICK_L
        ckr = PlayModes.CORNER_KICK_R

        # shorthand for whether left team or right team is free to act
        pm = self.wm.play_mode
        free_left = (pm == kil or pm == fkl or pm == ckl)
        free_right = (pm == kir or pm == fkr or pm == ckr)

        # return whether the opposing side is in a dead ball situation
        if self.wm.side == WorldModel.SIDE_L:
            return free_right
        else:
            return free_left

    def is_ball_kickable(self):
        """
        Tells us whether the ball is in reach of the current player.
        """

        # ball must be visible, not behind us, and within the kickable margin
        return (self.wm.ball is not None and
                self.wm.ball.distance is not None and
                self.wm.ball.distance <= self.wm.server_parameters.kickable_margin)
