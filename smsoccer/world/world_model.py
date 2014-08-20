import math
import random

import game_object
from smsoccer.util.geometric import euclidean_distance, angle_between_points
from smsoccer.world.parameters import ServerParameters


class WorldModel:
    """
    Holds and updates the model of the world as known from current and past
    data.
    """

    # constants for team sides
    SIDE_L = "l"
    SIDE_R = "r"

    class PlayModes:
        """
        Acts as a static class containing variables for all valid play modes.
        The string values correspond to what the referee calls the game modes.
        """

        BEFORE_KICK_OFF = "before_kick_off"
        PLAY_ON = "play_on"
        TIME_OVER = "time_over"
        KICK_OFF_L = "kick_off_l"
        KICK_OFF_R = "kick_off_r"
        KICK_IN_L = "kick_in_l"
        KICK_IN_R = "kick_in_r"
        FREE_KICK_L = "free_kick_l"
        FREE_KICK_R = "free_kick_r"
        CORNER_KICK_L = "corner_kick_l"
        CORNER_KICK_R = "corner_kick_r"
        GOAL_KICK_L = "goal_kick_l"
        GOAL_KICK_R = "goal_kick_r"
        DROP_BALL = "drop_ball"
        OFFSIDE_L = "offside_l"
        OFFSIDE_R = "offside_r"

        def __init__(self):
            raise NotImplementedError("Don't instantiate a PlayModes class,"
                                      " access it statically through WorldModel instead.")

    class RefereeMessages:
        """
        Static class containing possible non-mode messages sent by a referee.
        """

        # these are referee messages, not play modes
        FOUL_L = "foul_l"
        FOUL_R = "foul_r"
        GOALIE_CATCH_BALL_L = "goalie_catch_ball_l"
        GOALIE_CATCH_BALL_R = "goalie_catch_ball_r"
        TIME_UP_WITHOUT_A_TEAM = "time_up_without_a_team"
        TIME_UP = "time_up"
        HALF_TIME = "half_time"
        TIME_EXTENDED = "time_extended"

        # these are special, as they are always followed by '_' and an int of
        # the number of goals scored by that side so far.  these won't match
        # anything specifically, but goals WILL start with these.
        GOAL_L = "goal_l_"
        GOAL_R = "goal_r_"

        def __init__(self):
            raise NotImplementedError("Don't instantiate a RefereeMessages class,"
                                      " access it statically through WorldModel instead.")

    def __init__(self, action_handler):
        """
        Create the world model with default values and an ActionHandler class it
        can use to complete requested actions.
        """

        # we use the action handler to complete complex commands
        self.ah = action_handler

        # these variables store all objects for any particular game step
        self.ball = None
        self.flags = []
        self.goals = []
        self.players = []
        self.lines = []

        # the default position of this player, its home position
        self.home_point = (None, None)

        # scores for each side
        self.score_l = 0
        self.score_r = 0

        # the name of the agent's team
        self.team_name = None

        # handle player information, like uniform number and side
        self.side = None
        self.uniform_number = None

        # stores the most recent message heard
        self.last_message = None

        # the mode the game is currently in (default to not playing yet)
        self.play_mode = WorldModel.PlayModes.BEFORE_KICK_OFF

        # body state
        self.view_width = None
        self.view_quality = None
        self.stamina = None
        self.effort = None
        self.speed_amount = None
        self.speed_direction = None
        self.neck_direction = None

        # counts of actions taken so far
        self.kick_count = None
        self.dash_count = None
        self.turn_count = None
        self.say_count = None
        self.turn_neck_count = None
        self.catch_count = None
        self.move_count = None
        self.change_view_count = None

        # apparent absolute player coordinates and neck/body directions
        self.abs_coords = (None, None)
        self.abs_neck_dir = None
        self.abs_body_dir = None

        # create a new server parameter object for holding all server params
        self.server_parameters = ServerParameters()

    def triangulate_direction(self, flags, flag_dict):
        """
        Determines absolute view angle for the player given a list of visible
        flags.  We find the absolute angle to each flag, then return the average
        of those angles.  Returns 'None' if no angle could be determined.
        """

        # average all flag angles together and save that as absolute angle
        abs_angles = []
        for f in self.flags:
            # if the flag has useful data, consider it
            if f.distance is not None and f.flag_id in flag_dict:
                flag_point = flag_dict[f.flag_id]
                abs_dir = angle_between_points(self.abs_coords, flag_point)
                abs_angles.append(abs_dir)

        # return the average if available
        if len(abs_angles) > 0:
            return sum(abs_angles) / len(abs_angles)

        return None

    def triangulate_position(self, flags, flag_dict, angle_step=36):
        """
        Returns a best-guess position based on the triangulation via distances
        to all flags in the flag list given.  'angle_step' specifies the
        increments between angles for projecting points onto the circle
        surrounding a flag.
        """

        points = []
        for f in flags:
            # skip flags without distance information or without a specific id
            if f.distance is None or f.flag_id not in flag_dict:
                continue

            # generate points every 'angle_step' degrees around each flag,
            # discarding those off-field.
            for i in xrange(0, 360, angle_step):
                dy = f.distance * math.sin(math.radians(i))
                dx = f.distance * math.cos(math.radians(i))

                fcoords = flag_dict[f.flag_id]
                new_point = (fcoords[0] + dx, fcoords[1] + dy)

                # skip points with a coordinate outside the play boundaries
                if (new_point[0] > 60 or new_point[0] < -60 or
                            new_point[1] < -40 or new_point[1] > 40):
                    continue

                # add point to list of all points
                points.append(new_point)

        # get the dict of clusters mapped to centers
        clusters = self.cluster_points(points)

        # return the center that has the most points as an approximation to our
        # absolute position.
        center_with_most_points = (0, 0)
        max_points = 0
        for c in clusters:
            if len(clusters[c]) > max_points:
                center_with_most_points = c
                max_points = len(clusters[c])

        return center_with_most_points

    def cluster_points(self, points, num_cluster_iterations=15):
        """
        Cluster a set of points into a dict of centers mapped to point lists.
        Uses the k-means clustering algorithm with random initial centers and a
        fixed number of iterations to find clusters.
        """

        # generate initial random centers, ignoring identical ones
        centers = set([])
        for i in xrange(int(math.sqrt(len(points) / 2))):
            # a random coordinate somewhere within the field boundaries
            rand_center = (random.randint(-55, 55), random.randint(-35, 35))
            centers.add(rand_center)

        # cluster for some iterations before the latest result
        latest = {}
        cur = {}
        for i in xrange(num_cluster_iterations):
            # initialze cluster lists
            for c in centers:
                cur[c] = []

            # put every point into the list of its nearest cluster center
            for p in points:
                # get a list of (distance to center, center coords) tuples
                c_dists = map(lambda c: (euclidean_distance(c, p), c),
                              centers)

                # find the smallest tuple's c (second item)
                nearest_center = min(c_dists)[1]

                # add point to this center's cluster
                cur[nearest_center].append(p)

            # recompute centers
            new_centers = set([])
            for cluster in cur.values():
                tot_x = 0
                tot_y = 0

                # remove empty clusters
                if len(cluster) == 0:
                    continue

                # generate average center of cluster
                for p in cluster:
                    tot_x += p[0]
                    tot_y += p[1]

                # get average center and add to new centers set
                ave_center = (tot_x / len(cluster), tot_y / len(cluster))
                new_centers.add(ave_center)

            # move on to next iteration
            centers = new_centers
            latest = cur
            cur = {}

        # return latest cluster iteration
        return latest


    def process_new_info(self, ball, flags, goals, players, lines):
        """
        Update any internal variables based on the currently available
        information.  This also calculates information not available directly
        from server-reported messages, such as player coordinates.
        """

        # update basic information
        self.ball = ball
        self.flags = flags
        self.goals = goals
        self.players = players
        self.lines = lines

        # TODO: make all triangulate_* calculations more accurate

        # update the apparent coordinates of the player based on all flag pairs
        flag_dict = game_object.Flag.FLAG_COORDS
        self.abs_coords = self.triangulate_position(self.flags, flag_dict)

        # set the neck and body absolute directions based on flag directions
        self.abs_neck_dir = self.triangulate_direction(self.flags, flag_dict)

        # set body dir only if we got a neck dir, else reset it
        if self.abs_neck_dir is not None and self.neck_direction is not None:
            self.abs_body_dir = self.abs_neck_dir - self.neck_direction
        else:
            self.abs_body_dir = None

    def is_before_kick_off(self):
        """
        Tells us whether the game is in a pre-kickoff state.
        """

        return self.play_mode == WorldModel.PlayModes.BEFORE_KICK_OFF

    def is_kick_off_us(self):
        """
        Tells us whether it's our turn to kick off.
        """

        ko_left = WorldModel.PlayModes.KICK_OFF_L
        ko_right = WorldModel.PlayModes.KICK_OFF_R

        print self.play_mode

        # return whether we're on the side that's kicking off
        return (self.side == WorldModel.SIDE_L and self.play_mode == ko_left or
                self.side == WorldModel.SIDE_R and self.play_mode == ko_right)

    def is_dead_ball_them(self):
        """
        Returns whether the ball is in the other team's possession and it's a
        free kick, corner kick, or kick in.
        """

        # shorthand for verbose constants
        kil = WorldModel.PlayModes.KICK_IN_L
        kir = WorldModel.PlayModes.KICK_IN_R
        fkl = WorldModel.PlayModes.FREE_KICK_L
        fkr = WorldModel.PlayModes.FREE_KICK_R
        ckl = WorldModel.PlayModes.CORNER_KICK_L
        ckr = WorldModel.PlayModes.CORNER_KICK_R

        # shorthand for whether left team or right team is free to act
        pm = self.play_mode
        free_left = (pm == kil or pm == fkl or pm == ckl)
        free_right = (pm == kir or pm == fkr or pm == ckr)

        # return whether the opposing side is in a dead ball situation
        if self.side == WorldModel.SIDE_L:
            return free_right
        else:
            return free_left

    def is_ball_kickable(self):
        """
        Tells us whether the ball is in reach of the current player.
        """

        # ball must be visible, not behind us, and within the kickable margin
        return (self.ball is not None and
                self.ball.distance is not None and
                self.ball.distance <= self.server_parameters.kickable_margin)

    def get_ball_speed_max(self):
        """
        Returns the maximum speed the ball can be kicked at.
        """

        return self.server_parameters.ball_speed_max

    #todo Actuator
    def kick_to(self, point, extra_power=0.0):
        """
        Kick the ball to some point with some extra-power factor added on.
        extra_power=0.0 means the ball should stop at the given point, anything
        higher means it should have proportionately more speed.
        """

        # how far are we from the desired point?
        point_dist = euclidean_distance(self.abs_coords, point)

        # get absolute direction to the point
        abs_point_dir = angle_between_points(self.abs_coords, point)

        # get relative direction to point from body, since kicks are relative to
        # body direction.
        if self.abs_body_dir is not None:
            rel_point_dir = self.abs_body_dir - abs_point_dir

        # we do a simple linear interpolation to calculate final kick speed,
        # assuming a kick of power 100 goes 45 units in the given direction.
        # these numbers were obtained from section 4.5.3 of the documentation.
        # TODO: this will fail if parameters change, needs to be more flexible
        max_kick_dist = 45.0
        dist_ratio = point_dist / max_kick_dist

        # find the required power given ideal conditions, then add scale up by
        # difference between actual aceivable power and maximum power.
        required_power = dist_ratio * self.server_parameters.maxpower
        effective_power = self.get_effective_kick_power(self.ball,
                                                        required_power)
        required_power += 1 - (effective_power / required_power)

        # add more power!
        power_mod = 1.0 + extra_power
        power = required_power * power_mod

        # do the kick, finally
        self.ah.kick(rel_point_dir, power)

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
        kick_power = max(min(power, self.server_parameters.maxpower),
                         self.server_parameters.minpower)

        # scale it by the kick_power rate
        kick_power *= self.server_parameters.kick_power_rate

        # now we calculate the real effective power...
        a = 0.25 * (ball.direction / 180)
        b = 0.25 * (ball.distance / self.server_parameters.kickable_margin)

        # ...and then return it
        return 1 - a - b

    #todo Actuator
    def turn_neck_to_object(self, obj):
        """
        Turns the player's neck to a given object.
        """

        self.ah.turn_neck(obj.direction)


    def get_distance_to_point(self, point):
        """
        Returns the linear distance to some point on the field from the current
        point.
        """

        return euclidean_distance(self.abs_coords, point)

    #todo Actuator
    def turn_body_to_point(self, point):
        """
        Turns the agent's body to face a given point on the field.
        """

        # calculate absolute direction to point
        abs_point_dir = angle_between_points(self.abs_coords, point)

        # subtract from absolute body direction to get relative angle
        relative_dir = self.abs_body_dir - abs_point_dir

        # turn to that angle
        self.ah.turn(relative_dir)

    def get_object_absolute_coords(self, obj):
        """
        Determines the absolute coordinates of the given object based on the
        agent's current position.  Returns None if the coordinates can't be
        calculated.
        """

        # we can't calculate this without a distance to the object
        if obj.distance is None:
            return None

        # get the components of the vector to the object
        dx = obj.distance * math.cos(obj.direction)
        dy = obj.distance * math.sin(obj.direction)

        # return the point the object is at relative to our current position
        return self.abs_coords[0] + dx, self.abs_coords[1] + dy

    #todo Actuator
    def teleport_to_point(self, point):
        """
        Teleport the player to a given (x, y) point using the 'move' command.
        """

        self.ah.move(point[0], point[1])

    #todo Actuator
    def align_neck_with_body(self):
        """
        Turns the player's neck to be in line with its body, making the angle
        between the two 0 degrees.
        """

        # neck angle is relative to body, so we turn it back the inverse way
        if self.neck_direction is not None:
            self.ah.turn_neck(self.neck_direction * -1)

    def get_nearest_teammate_to_point(self, point):
        """
        Returns the uniform number of the fastest teammate to some point.
        """

        # holds tuples of (player dist to point, player)
        distances = []
        for p in self.players:
            # skip enemy and unknown players
            if p.side != self.side:
                continue

            # find their absolute position
            p_coords = self.get_object_absolute_coords(p)

            distances.append((euclidean_distance(point, p_coords), p))

        # return the nearest known teammate to the given point
        nearest = min(distances)[1]
        return nearest

    def get_stamina(self):
        """
        Returns the agent's current stamina amount.
        """

        return self.stamina

    def get_stamina_max(self):
        """
        Returns the maximum amount of stamina a player can have.
        """

        return self.server_parameters.stamina_max

    def turn_body_to_object(self, obj):
        """
        Turns the player's body to face a particular object.
        """

        self.ah.turn(obj.direction)




