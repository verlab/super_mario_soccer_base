import math

import game_object
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
        self.old_abs_coords = (0, 0)

        # create a new server parameter object for holding all server params
        self.server_parameters = ServerParameters()

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

        self.old_abs_coords = self.abs_coords[:] if self.abs_coords is not None else self.old_abs_coords
        self.abs_coords = triangulate_position(self.flags, flag_dict)

        if self.abs_coords is None:
            self.abs_coords = self.old_abs_coords

            print "Cannot triangulate localization, taking the last one"

        # set the neck and body absolute directions based on flag directions
        self.abs_neck_dir = triangulate_direction(self.abs_coords, self.flags, flag_dict)
        self.abs_neck_dir = cut_angle(self.abs_neck_dir)

        # set body dir only if we got a neck dir, else reset it
        if self.abs_neck_dir is not None and self.neck_direction is not None:
            self.abs_body_dir = self.abs_neck_dir - self.neck_direction
        else:
            self.abs_body_dir = None

    def is_before_kick_off(self):
        """
        Tells us whether the game is in a pre-kickoff state.
        """

        return self.play_mode == PlayModes.BEFORE_KICK_OFF

    def is_kick_off_us(self):
        """
        Tells us whether it's our turn to kick off.
        """

        ko_left = PlayModes.KICK_OFF_L
        ko_right = PlayModes.KICK_OFF_R

        print self.play_mode

        # return whether we're on the side that's kicking off
        return (self.side == WorldModel.SIDE_L and self.play_mode == ko_left or
                self.side == WorldModel.SIDE_R and self.play_mode == ko_right)

    def get_ball_speed_max(self):
        """
        Returns the maximum speed the ball can be kicked at.
        """

        return self.server_parameters.ball_speed_max

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
        dx = obj.distance * math.cos(math.radians(obj.direction))
        dy = obj.distance * math.sin(math.radians(obj.direction))
        print dx, dy

        # return the point the object is at relative to our current position
        return self.abs_coords[0] + dx, self.abs_coords[1] + dy

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