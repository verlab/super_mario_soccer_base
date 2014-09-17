import math

import game_object
from smsoccer.localization.filter.particlefilter import ParticleFilter
from smsoccer.localization.localization import triangulate_position, triangulate_direction
from smsoccer.util.geometric import cut_angle
from smsoccer.world.parameters import ServerParameters


class WorldModel:
    """
    Holds and updates the model of the world as known from current and past
    data.
    """

    # constants for team sides
    SIDE_L = "l"
    SIDE_R = "r"


    def __init__(self, action_handler, filter_robot_loc=True):
        """
        Create the world model with default values and an ActionHandler class it
        can use to complete requested actions.
        :param action_handler:
        :param filter_robot_loc: filter robot localization
        """

        # we use the action handler to complete complex commands
        self.filter_robot_loc = filter_robot_loc
        self.ah = action_handler

        # these variables store all objects for any particular game step
        self.ball = None
        self.flags = []
        self.goals = []
        self.players = []

        # dict of dicts, first level indexed with 'friends'/'foes', 2nd level with uniform number
        self.players_persistent = {
            #expands 10 None parameters with * [None]*10
            # range: [1,2,...,11] (shirt numbers)
            'friends': {num: game_object.Player(*[None] * 10) for num in range(1, 12)},
            'foes': {num: game_object.Player(*[None] * 10) for num in range(1, 12)}
        }

        self.lines = []

        # Received message
        self.prev_message = None

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
        self.play_mode = PlayModes.BEFORE_KICK_OFF

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
        self.abs_coords = None
        self.abs_neck_dir = None
        self.abs_body_dir = None

        # Simulation time
        self.sim_time = None
        # self.old_abs_coords = (0, 0)
        # self.old_direction = 0

        # Speed
        self.vx, self.vy = 0, 0
        # create a new server parameter object for holding all server params
        self.server_parameters = ServerParameters()

        self.team_message_queue = []

        if self.filter_robot_loc:
            # Particle filter for robot localization
            self.pf = ParticleFilter()


    def process_new_info(self, ball, flags, goals, players, lines, sim_time):
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

        #updates available info in currently seen players
        team = None
        number = None
        for player in self.players:
            team = 'friends' if player.side and player.side == self.side else 'foes'

            number = player.uniform_number if player.uniform_number else None

            #discards if i don't know who this player is
            if team is None or number is None:
                continue

            #updates persistent player with available information
            self.players_persistent[team][number] = player
            #print 'player updated!'


        x1, y1 = self.old_abs_coords[:]
        #updates available info in currently seen players
        team = None
        number = None
        # updates available info in currently seen players
        for player in self.players:
            team = 'friends' if player.side and player.side == self.side else 'foes'

            number = player.uniform_number if player.uniform_number else None

            #discards if i don't know who this player is
            if team is None or number is None:
                continue

            #updates persistent player with available information
            self.players_persistent[team][number] = player
            #print 'player updated!'


        # ##################### Location #########
        # Take only good flags
        gflags = [f for f in flags if
                  f.distance is not None and f.direction is not None and f.flag_id is not None]
        #gflags = sorted(gflags, key=lambda x: x.distance)
        if len(gflags) < 2:
            # Error in triangulation
            self.abs_coords = None
            self.abs_neck_dir = None
            # print "Not enough flags for localization"
        else:
            self.abs_coords = triangulate_position(gflags)

            if self.abs_coords is not None:
                # set the neck and body absolute directions based on flag directions
                self.abs_neck_dir = triangulate_direction(self.abs_coords, gflags)
                self.abs_neck_dir = cut_angle(self.abs_neck_dir)
            else:
                self.abs_neck_dir = None

        # set body dir only if we got a neck dir, else reset it
        if self.abs_neck_dir is not None and self.neck_direction is not None:
            self.abs_body_dir = self.abs_neck_dir - self.neck_direction
        else:
            self.abs_body_dir = None

        # TODO ##################### Speed #########333
        # if sim_time > self.sim_time > 0:
        # x2, y2 = self.abs_coords[:]
        # # Velocity in x and y
        # self.vx, self.vy = x2 - x1, y2 - y1

        self.sim_time = sim_time

    def is_ball_in_defense(self):
        """
        Returns whether the ball is on the defensive field
        :return: bool
        """
        # conservative behavior: assumes ball in defense if i can't see it
        if self.ball is None:
            return True

        #returns True if ball.x is less than zero
        else:
            if self.get_object_absolute_coords(self.ball) is None:
                return True
            else:
                return self.get_object_absolute_coords(self.ball)[0] < 0

    def is_kick_in(self):
        """
        Returns whether it is a kick-in situation (for either us or adversary)
        :return:
        """
        return self.play_mode in [PlayModes.KICK_IN_L, PlayModes.KICK_IN_R]

    def is_kick_in_us(self):
        """
        Returns whether it is a kick-in for us
        :return:
        """
        ki_l, ki_r = PlayModes.KICK_IN_L, PlayModes.KICK_IN_R  # just aliases

        return (self.play_mode == ki_l and self.side == self.SIDE_L) or \
               (self.play_mode == ki_r and self.side == self.SIDE_R)

    def is_goal_kick(self):
        """
        Returns whether it is a goal kick (for either us or adversary)
        :return:
        """
        return self.play_mode in [PlayModes.GOAL_KICK_L, PlayModes.GOAL_KICK_R]

    def is_goal_kick_us(self):
        """
        Returns whether it is a goal kick for us
        :return:
        """
        gk_l, gk_r = PlayModes.GOAL_KICK_L, PlayModes.GOAL_KICK_R  # just aliases

        return (self.play_mode == gk_l and self.side == self.SIDE_L) or \
               (self.play_mode == gk_r and self.side == self.SIDE_R)

    def is_corner_kick(self):
        """
        Returns whether it is a corner kick (for either us or adversary)
        :return:
        """
        return self.play_mode in [PlayModes.CORNER_KICK_L, PlayModes.CORNER_KICK_R]

    def is_corner_kick_us(self):
        """
        Returns whether it is a corner kick for us
        :return:
        """
        ck_l, ck_r = PlayModes.CORNER_KICK_L, PlayModes.CORNER_KICK_R  # just aliases

        return (self.play_mode == ck_l and self.side == self.SIDE_L) or \
               (self.play_mode == ck_r and self.side == self.SIDE_R)

    def is_free_kick(self):
        """
        Returns whether it is a free kick or not (for either us or adversary)
        """
        return self.play_mode in [PlayModes.FREE_KICK_L, PlayModes.FREE_KICK_R]

    def is_free_kick_us(self):
        """
        Returns whether it is a free kick for us
        """
        fk_l, fk_r = PlayModes.FREE_KICK_L, PlayModes.FREE_KICK_R  # just aliases

        return (self.play_mode == fk_l and self.side == self.SIDE_L) or \
               (self.play_mode == fk_r and self.side == self.SIDE_R)

    def is_before_kick_off(self):
        """
        Tells us whether the game is in a pre-kickoff state.
        """

        return self.play_mode == PlayModes.BEFORE_KICK_OFF

    def is_kick_off_us(self):
        """
        Tells us whether it is a kick off for us
        """

        ko_left = PlayModes.KICK_OFF_L
        ko_right = PlayModes.KICK_OFF_R

        first_cycle = self.sim_time is None or self.sim_time == 0

        # return whether we're on the side that's kicking off or if we are on the left side when game begins
        return (first_cycle and self.side == WorldModel.SIDE_L) or \
               (self.side == WorldModel.SIDE_L and self.play_mode == ko_left or
                self.side == WorldModel.SIDE_R and self.play_mode == ko_right)

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

    def get_object_absolute_coords(self, obj, reference=None):
        """
        Determines the absolute coordinates of the given object based on the
        agent's current position.  Returns None if the coordinates can't be
        calculated.
        """
        if reference is None:
            reference = self.abs_coords

        # we can't calculate this without a distance to the object
        if obj.distance is None:
            return None

        # get the components of the vector to the object
        dx = obj.distance * math.cos(math.radians(obj.direction))
        dy = obj.distance * math.sin(math.radians(obj.direction))
        # print dx, dy

        # return the point the object is at relative to our current position
        return reference[0] + dx, reference[1] + dy

    def get_stamina_max(self):
        """
        Returns the maximum amount of stamina a player can have.
        """

        return self.sm.server_parameters.stamina_max


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