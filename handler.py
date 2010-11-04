import message_parser
import sp_exceptions
import game_object

class MessageHandler:
    """
    Handles all incoming messages from the server.  Parses their data and puts
    it into the given WorldModel.

    All '_handle_*' functions deal with their appropriate message types
    as received from a server.  This allows adding a message handler to be as
    simple as adding a new '_handle_*' function to this object.
    """

    def __init__(self, world_model):
        self.world_model = world_model

    def handle_message(self, msg):
        """
        Takes a raw message direct from the server, parses it, and stores its
        data within this object.
        """
        
        # get all the expressions contained in the given message
        parsed = message_parser.parse(msg)
        
        # this is the name of the function that should be used to handle
        # this message type.  we pull it from this object dynamically to
        # avoid having a huge if/elif/.../else statement. this should be both
        # faster and more flexible (dict lookup is really fast in python).
        msg_func = "_handle_%s" % parsed[0]

        if hasattr(self, msg_func):
            # call the appropriate function with this message
            getattr(self, msg_func).__call__(parsed)

        # throw an exception if we don't know about the given message type
        else:
            m = "Can't handle message type '%s', function '%s' not found."
            raise sp_exceptions.MessageTypeError(m % (parsed[0], msg_func))

    def _handle_see(self, msg):
        """
        Parses visual information in a message and turns it into useful data.
        """

        print "see:", msg[1:]
        print

    def _handle_hear(self, msg):
        """
        Parses audible information and turns it into useful information.
        """

        print "hear:", msg[1:]
        print

    def _handle_sense_body(self, msg):
        """
        Deals with the agent's body model information.
        """

        print "sense_body:", msg[1:]
        print

    def _handle_player_param(self, msg):
        """
        Deals with player parameter information.
        """

        print "player_param:", msg[1:]
        print

    def _handle_player_type(self, msg):
        """
        Handles player type information.
        """

        print "player_type:", msg[1:]
        print

    def _handle_server_param(self, msg):
        """
        Stores server parameter information.
        """

        print "server_param:", msg[1:]
        print

    def _handle_init(self, msg):
        """
        Deals with initialization messages sent by the server.
        """

        print "init:", msg[1:]
        print
    
    def _handle_error(self, msg):
        """
        Deals with error messages by raising them as exceptions.
        """

        m = "Server returned an error: '%s'" % msg[1]
        print sp_exceptions.SoccerServerError(m)

    def _handle_warning(self, msg):
        """
        Deals with warnings issued by the server.
        """
        
        m = "Server issued a warning: '%s'" % msg[1]
        print sp_exceptions.SoccerServerWarning(m)

class ActionHandler:
    """
    Provides facilities for sending commands to the soccer server.  Contains all
    possible commands that can be sent, as well as everything needed to send
    them.
    """

    def __init__(self, server_socket):
        """
        Save the socket that connects us to the soccer server to allow us to
        send it commands.
        """
        
        self.sock = server_socket
