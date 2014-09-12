import collections

import messageparser


# should we print messages received from the server?
from smsoccer.communication.teammessage import TeamMessage
from smsoccer.communication.worldparser import parse_message_see
from smsoccer.util import sp_exceptions
from smsoccer.world import game_object
from smsoccer.world.world_model import WorldModel, RefereeMessages

PRINT_SERVER_MESSAGES = False
TEAM_QUEUE_MSG_CAPACITY = 5


class MessageHandler:
    """
    Handles all incoming messages from the server.  Parses their data and puts
    it into the given WorldModel.

    All '_handle_*' functions deal with their appropriate message types
    as received from a server.  This allows adding a message handler to be as
    simple as adding a new '_handle_*' function to this object.
    """

    # an inner class used for creating named tuple 'hear' messages
    Message = collections.namedtuple("Message", "time sender message")

    def __init__(self, world_model):
        self.wm = world_model

    def handle_message(self, msg):
        """
        Takes a raw message direct from the server, parses it, and stores its
        data in the world and body model objects given at init.  Returns the
        type of message received.
        """

        # get all the expressions contained in the given message
        parsed = messageparser.parse(msg)

        if PRINT_SERVER_MESSAGES:
            print msg
            # print parsed[0] + ":", parsed[1:], "\n"

        # this is the name of the function that should be used to handle
        # this message type.  we pull it from this object dynamically to
        # avoid having a huge if/elif/.../else statement.
        msg_func = "_handle_%s" % parsed[0]

        if hasattr(self, msg_func):
            # call the appropriate function with this message
            getattr(self, msg_func).__call__(parsed)

        # throw an exception if we don't know about the given message type
        else:
            m = "Can't handle message type '%s', function '%s' not found."
            # FIXME raising will kill the agent.
            raise sp_exceptions.MessageTypeError(m % (parsed[0], msg_func))
            # print sp_exceptions.MessageTypeError(m % (parsed[0], msg_func))

        # return the type of message received
        return parsed[0]

    def _handle_see(self, msg):
        """
        Parses visual information in a message and turns it into useful data.

        This comes to us as a list of lists.  Each list contains another list as
        its first element, the contents of which describe a particular object.
        The other items of the list are data pertaining to the object.  We parse
        each list into its own game object, then insert those game objects into
        the world model.
        """

        # the simulation cycle of the soccer server
        self.wm.last_message = msg

        new_ball, new_flags, new_goals, new_players, new_lines, sim_time = parse_message_see(msg, self.wm)


        # tell the WorldModel to update any internal variables based on the
        # newly gleaned information.
        self.wm.process_new_info(new_ball, new_flags, new_goals, new_players,
                                 new_lines, sim_time)

    def _handle_hear(self, msg):
        """
        Parses audible information and turns it into useful information.
        """
        time_recvd = msg[1]  # server cycle when message was heard
        sender = msg[2]  # name (or direction) of who sent the message
        message = msg[3]  # message string

        # ignore messages sent by self (NOTE: would anybody really want these?)
        if sender == "self":
            return

        # handle messages from the referee, to update game state
        elif sender == "referee":
            # change the name for convenience's sake
            mode = message

            # deal first with messages that shouldn't be passed on to the agent

            # keep track of scores by setting them to the value reported.  this
            # precludes any possibility of getting out of sync with the server.
            if mode.startswith(RefereeMessages.GOAL_L):
                # split off the number, the part after the rightmost '_'
                self.wm.score_l = int(mode.rsplit("_", 1)[1])
                return
            elif mode.startswith(RefereeMessages.GOAL_R):
                self.wm.score_r = int(mode.rsplit("_", 1)[1])
                return

            # ignore these messages, but pass them on to the agent. these don't
            # change state but could still be useful.
            elif (mode == RefereeMessages.FOUL_L or
                          mode == RefereeMessages.FOUL_R or
                          mode == RefereeMessages.GOALIE_CATCH_BALL_L or
                          mode == RefereeMessages.GOALIE_CATCH_BALL_R or
                          mode == RefereeMessages.TIME_UP_WITHOUT_A_TEAM or
                          mode == RefereeMessages.HALF_TIME or
                          mode == RefereeMessages.TIME_EXTENDED):

                # messages are named 3-tuples of (time, sender, message)
                ref_msg = self.Message(time_recvd, sender, message)

                # pass this message on to the player and return
                self.wm.last_message = ref_msg
                return

            # deal with messages that indicate game mode, but that the agent
            # doesn't need to know about specifically.
            else:
                # set the mode to the referee reported mode string
                self.wm.play_mode = mode
                return
        else:
            # Opponents message
            if msg[3] == 'opp':
                # Opponents messages are not of interest
                return

            time = msg[1]
            ### For player
            if len(msg)>4:

                who = msg[4]
                content = msg[5]
            else: # Coach
                who = msg[2]
                content = msg[3]

            team_msg = TeamMessage(time, who, content)
            # Last message first in the queue.
            self.wm.team_message_queue.insert(0, team_msg)

            if len(self.wm.team_message_queue) > TEAM_QUEUE_MSG_CAPACITY:
                    self.wm.team_message_queue = self.wm.team_message_queue[:TEAM_QUEUE_MSG_CAPACITY]


        # all other messages are treated equally
        # else:
        # # update the model's last heard message
        # new_msg = MessageHandler.Message(time_recvd, sender, message)
        #     self.wm.prev_message = new_msg

    def _handle_sense_body(self, msg):
        """
        Deals with the agent's body model information.
        """

        # update the body model information when received. each piece of info is
        # a list with the first item as the name of the data, and the rest as
        # the values.
        for info in msg[2:]:
            name = info[0]
            values = info[1:]

            if name == "view_mode":
                self.wm.view_quality = values[0]
                self.wm.view_width = values[1]
            elif name == "stamina":
                self.wm.stamina = values[0]
                self.wm.effort = values[1]
            elif name == "speed":
                self.wm.speed_amount = values[0]
                self.wm.speed_direction = values[1]
            elif name == "head_angle":
                self.wm.neck_direction = values[0]

            # these update the counts of the basic actions taken
            elif name == "kick":
                self.wm.kick_count = values[0]
            elif name == "dash":
                self.wm.dash_count = values[0]
            elif name == "turn":
                self.wm.turn_count = values[0]
            elif name == "say":
                self.wm.say_count = values[0]
            elif name == "turn_neck":
                self.wm.turn_neck_count = values[0]
            elif name == "catch":
                self.wm.catch_count = values[0]
            elif name == "move":
                self.wm.move_count = values[0]
            elif name == "change_view":
                self.wm.change_view_count = values[0]

            # we leave unknown values out of the equation
            else:
                pass

    def _handle_change_player_type(self, msg):
        """
        Handle player change messages.
        """

    def _handle_player_param(self, msg):
        """
        Deals with player parameter information.
        """

    def _handle_player_type(self, msg):
        """
        Handles player type information.
        """

    def _handle_server_param(self, msg):
        """
        Stores server parameter information.
        """

        # each list is two items: a value name and its value.  we add them all
        # to the ServerParameters class inside WorldModel programmatically.
        for param in msg[1:]:
            # put all [param, value] pairs into the server settings object
            # by setting the attribute programmatically.
            if len(param) != 2:
                continue

            # the parameter and its value
            key = param[0]
            value = param[1]

            # set the attribute if it was accounted for, otherwise alert the user
            if hasattr(self.wm.server_parameters, key):
                setattr(self.wm.server_parameters, key, value)
            else:
                raise AttributeError("Couldn't find a matching parameter in "
                                     "ServerParameters class: '%s'" % key)

    def _handle_init(self, msg):
        """
        Deals with initialization messages sent by the server.
        """
        # set the player's uniform number, side, and the play mode as returned
        # by the server directly after connecting.
        side = msg[1]

        # if coach
        if msg[2] == 'ok':
            return

        uniform_number = msg[2]
        play_mode = msg[3]

        self.wm.side = side
        self.wm.uniform_number = uniform_number
        self.wm.play_mode = play_mode


    def _handle_error(self, msg):
        """
        Deals with error messages by raising them as exceptions.
        """

        m = "Server returned an error: '%s'" % msg[1]
        raise sp_exceptions.SoccerServerError(m)

    def _handle_warning(self, msg):
        """
        Deals with warnings issued by the server.
        """

        m = "Server issued a warning: '%s'" % msg[1]
        print sp_exceptions.SoccerServerWarning(m)

    # ####### Coach
    def _handle_ok(self, msg):
        """
        Response of (look)
        :param msg:
        """
        print msg

    def _handle_see_global(self, msg):
        """
        Automatic message after (eye on)
        :param msg: (see_global 0 ((g r) 52.5 0) ((g l) -52.5 0) ((b) 0 0 0 0) ((p "default" 1) -50 0 0 0 0 0)) 
        """
        new_ball, new_flags, new_goals, new_players, new_lines, sim_time = parse_message_see(msg, self.wm)
        # tell the WorldModel to update any internal variables based on the
        # newly gleaned information.
        self.wm.process_new_info(new_ball, new_flags, new_goals, new_players,
                                 new_lines, sim_time)