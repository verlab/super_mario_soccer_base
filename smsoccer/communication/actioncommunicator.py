import collections
import Queue as queue

LOOK_MESSAGE = '(look)'

EYE_MESSAGE = '(eye %s)'

VIEW_QUALITY_LOW = "low"
VIEW_QUALITY_HIGH = "high"
VIEW_WIDTH_NARROW = "narrow"
VIEW_WIDTH_NORMAL = "normal"
VIEW_WIDTH_WIDE = "wide"

## Messages to server
DASH_MESSAGE = "(dash %.10f)"
TURN_MESSAGE = "(turn %.10f)"
MOVE_MESSAGE = "(move %.10f %.10f)"
TURN_NECK_MESSAGE = "(turn_neck %.10f)"
SAY_MESSAGE = "(say %s)"
CATCH_MESSAGE = "(catch %.10f)"
KICK_MESSAGE = "(kick %.10f %.10f)"
VIEW_QUALITY_MESSAGE = "(change_view %s %s)"

# should we print commands sent to the server?
PRINT_SENT_COMMANDS = False


class ActionCommunicator(object):
    """
    Provides facilities for sending commands to the soccer server.  Contains all
    possible commands that can be sent, as well as everything needed to send
    them.  All basic command methods are aliases for placing that command in the
    internal queue and sending it at the appropriate time.
    """

    class CommandType:
        """
        A static class that defines all basic command types.
        """

        # whether the command can only be sent once per cycle or not
        TYPE_PRIMARY = 0
        TYPE_SECONDARY = 1

        # command types corresponding to valid commands to send to the server
        CATCH = "catch"
        CHANGE_VIEW = "change_view"
        DASH = "dash"
        KICK = "kick"
        MOVE = "move"
        SAY = "say"
        SENSE_BODY = "sense_body"
        TURN = "turn"
        TURN_NECK = "turn_neck"

        def __init__(self):
            raise NotImplementedError("Can't instantiate a CommandType, access "
                                      "its members through ActionHandler instead.")

    # a command for our queue containing an id and command text
    Command = collections.namedtuple("Command", "cmd_type text")

    def __init__(self, server_socket):
        """
        Save the socket that connects us to the soccer server to allow us to
        send it commands.
        """

        self.sock = server_socket

        # this contains all requested actions for the current and future cycles
        self.q = queue.Queue()

    def send_commands(self):
        """
        Sends all the enqueued commands.
        """

        # we only send the most recent primary command
        primary_cmd = None

        # dequeue all enqueued commands and send them
        while 1:
            try:
                cmd = self.q.get_nowait()
            except queue.Empty:
                break

            # save the most recent primary command and send it at the very end
            if cmd.cmd_type == ActionCommunicator.CommandType.TYPE_PRIMARY:
                primary_cmd = cmd
            # send other commands immediately
            else:
                if PRINT_SENT_COMMANDS:
                    print "sent:", cmd.text, "\n"

                self.sock.send(cmd.text)

            # indicate that we finished processing a command
            self.q.task_done()

        # send the saved primary command, if there was one
        if primary_cmd is not None:
            if PRINT_SENT_COMMANDS:
                print "sent:", primary_cmd.text, "\n"

            self.sock.send(primary_cmd.text)

    def move(self, x, y):
        """
        Teleport the player to some location on the field.  Only works before
        play begins, ie. pre-game, before starting again at half-time, and
        post-goal.  If an invalid location is specified, player is teleported to
        a random location on their side of the field.
        """

        msg = MOVE_MESSAGE % (x, y)

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def turn(self, relative_degrees):
        """
        Turns the player's body some number of degrees relative to its current
        angle.
        """

        if relative_degrees < -180: relative_degrees = -180
        if relative_degrees > 180: relative_degrees = 180

        # disallow unreasonable turning
        assert -180 <= relative_degrees <= 180

        msg = TURN_MESSAGE % relative_degrees

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def dash(self, power):
        """
        Accelerate the player in the direction its body currently faces.
        """

        msg = DASH_MESSAGE % power

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def kick(self, power, relative_direction):
        """
        Accelerates the ball with the given power in the given direction,
        relative to the current direction of the player's body.
        """

        msg = KICK_MESSAGE % (power, relative_direction)

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def catch(self, relative_direction):
        """
        Attempts to catch the ball and put it in the goalie's hand.  The ball
        remains there until the goalie kicks it away.
        """

        msg = CATCH_MESSAGE % relative_direction

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def say(self, message):
        """
        Says something to other players on the field.  Messages are restricted
        in length, but that isn't enforced here.
        """

        msg = SAY_MESSAGE % message

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_SECONDARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)

    def turn_neck(self, relative_direction):
        """
        Rotates the player's neck relative to its previous direction.  Neck
        angle is relative to body angle.
        """

        msg = TURN_NECK_MESSAGE % relative_direction

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_SECONDARY
        cmd = ActionCommunicator.Command(cmd_type, msg)

        self.q.put(cmd)


    def change_view_quality(self, width, quality):
        """
        Change view quality. View frequency depends on these parameters,
        look at equation (4.13) of the manual.
        :param width: narrow or normal
        :param quality: high or low
        """
        msg = VIEW_QUALITY_MESSAGE % (width, quality)

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_SECONDARY
        cmd = ActionCommunicator.Command(cmd_type, msg)
        self.q.put(cmd)



    ############# COACH ############
    def eye_on(self, enable):
        on_off = "on" if enable else "off"
        msg = EYE_MESSAGE % on_off

        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, msg)
        # Send the message directly.
        self.sock.send(cmd.text)

    def look(self):
        # create the command object for insertion into the queue
        cmd_type = ActionCommunicator.CommandType.TYPE_PRIMARY
        cmd = ActionCommunicator.Command(cmd_type, LOOK_MESSAGE)
        self.q.put(cmd)

        self.sock.send(cmd.text)


