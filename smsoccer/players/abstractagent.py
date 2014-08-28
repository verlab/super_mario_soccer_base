#!/usr/bin/env python

import threading
import time

from smsoccer.communication.actioncommunicator import ActionCommunicator
from smsoccer.communication import sock
from smsoccer.communication.messagehandler import MessageHandler
from smsoccer.util import sp_exceptions
from smsoccer.world.world_model import WorldModel


BYE_MESSAGE = "(bye)"
INIT_MESSAGE = "(init %s (version %d)%s)"


class AbstractAgent(object):
    """
    Abstract agent to be extended by all the players.
    """

    def __init__(self, goalie=False):
        # whether we're connected to a server yet or not
        self.goalie = goalie
        self.__connected = False

        # set all variables and important objects to appropriate values for
        # pre-connect state.

        # the socket used to communicate with the server
        self.__sock = None

        # models and the message handler for parsing and storing information
        self.wm = None
        self.msg_handler = None

        # parse thread and control variable
        self.__parsing = False
        self._msg_thread = None

        self.__thinking = False  # think thread and control variable
        self._think_thread = None

        # whether we should run the think method
        self.__should_think_on_data = False

        # whether we should send commands
        self.__send_commands = False

        self.in_kick_off_formation = False

        # Goal position depends on the side
        self.goal_pos = None


    def connect(self, host, port, teamname, version=15.1):
        """
        Gives us a connection to the server as one player on a team.  This
        immediately connects the agent to the server and starts receiving and
        parsing the information it sends.
        """

        # if already connected, raise an error since user may have wanted to
        # connect again to a different server.
        if self.__connected:
            msg = "Cannot connect while already connected, disconnect first."
            raise sp_exceptions.AgentConnectionStateError(msg)

        # the pipe through which all of our communication takes place
        self.__sock = sock.Socket(host, port)

        # our models of the world and our body
        self.wm = WorldModel(ActionCommunicator(self.__sock))

        # set the team name of the world model to the given name
        self.wm.team_name = teamname

        # handles all messages received from the server
        self.msg_handler = MessageHandler(self.wm)

        # set up our threaded message receiving system
        self.__parsing = True  # tell thread that we're currently running
        self._msg_thread = threading.Thread(target=self.__message_loop,
                                             name="message_loop")
        self._msg_thread.daemon = True  # dies when parent thread dies

        # start processing received messages. this will catch the initial server
        # response and all subsequent communication.
        self._msg_thread.start()

        # send the init message and allow the message handler to handle further
        # responses.
        init_address = self.__sock.address

        with_goalie = " (goalie)" if self.goalie else ""
        # Send init message
        self.__sock.send(INIT_MESSAGE % (teamname, version, with_goalie))

        # wait until the socket receives a response from the server and gets its
        # assigned port.
        while self.__sock.address == init_address:
            time.sleep(0.0001)

        # create our thinking thread.  this will perform the actions necessary
        # to play a game of robo-soccer.
        self.__thinking = False
        self._think_thread = threading.Thread(target=self.__think_loop,
                                               name="think_loop")
        self._think_thread.daemon = True

        # set connected state.  done last to prevent state inconsistency if
        # something goes wrong beforehand.
        self.__connected = True

        # determine the enemy goal position
        self.goal_pos = (52.5, 0)

        return self

    def play(self):
        """
        Kicks off the thread that does the agent's thinking, allowing it to play
        during the game.  Throws an exception if called while the agent is
        already playing.
        """

        # ensure we're connected before doing anything
        if not self.__connected:
            msg = "Must be connected to a server to begin play."
            raise sp_exceptions.AgentConnectionStateError(msg)

        # throw exception if called while thread is already running
        if self.__thinking:
            raise sp_exceptions.AgentAlreadyPlayingError(
                "Agent is already playing.")

        # tell the thread that it should be running, then start it
        self.__thinking = True
        self.__should_think_on_data = True

        # initialization
        self.initialization()
        # start thinking
        self._think_thread.start()

        return self

    def disconnect(self):
        """
        Tell the loop threads to stop and signal the server that we're
        disconnecting, then join the loop threads and destroy all our inner
        methods.

        Since the message loop thread can conceivably block indefinitely while
        waiting for the server to respond, we only allow it (and the think loop
        for good measure) a short time to finish before simply giving up.

        Once an agent has been disconnected, it is 'dead' and cannot be used
        again.  All of its methods get replaced by a method that raises an
        exception every time it is called.
        """

        # don't do anything if not connected
        if not self.__connected:
            return

        # tell the loops to terminate
        self.__parsing = False
        self.__thinking = False

        # tell the server that we're quitting
        self.__sock.send(BYE_MESSAGE)

        # tell our threads to join, but only wait briefly for them to do so.
        # don't join them if they haven't been started (this can happen if
        # disconnect is called very quickly after connect).
        if self._msg_thread.is_alive():
            self._msg_thread.join(0.01)

        if self._think_thread.is_alive():
            self._think_thread.join(0.01)

        # reset all standard variables in this object.  self.__connected gets
        # reset here, along with all other non-user defined internal variables.
        AbstractAgent.__init__(self)

        return self

    def __message_loop(self):
        """
        Handles messages received from the server.

        This SHOULD NOT be called externally, since it's used as a threaded loop
        internally by this object.  Calling it externally is a BAD THING!
        """

        # loop until we're told to stop
        while self.__parsing:
            # receive message data from the server and pass it along to the
            # world model as-is.  the world model parses it and stores it within
            # itself for perusal at our leisure.
            raw_msg = self.__sock.recv()
            msg_type = self.msg_handler.handle_message(raw_msg)

            # we send commands all at once every cycle, ie. whenever a
            # 'sense_body' command is received
            if msg_type == ActionCommunicator.CommandType.SENSE_BODY:
                self.__send_commands = True

            # flag new data as needing the think loop's attention
            self.__should_think_on_data = True

    def __think_loop(self):
        """
        Performs world model analysis and sends appropriate commands to the
        server to allow the agent to participate in the current game.

        Like the message loop, this SHOULD NOT be called externally.  Use the
        play method to start play, and the disconnect method to end it.
        """

        while self.__thinking:
            # tell the ActionHandler to send its enqueue messages if it is time
            if self.__send_commands:
                self.__send_commands = False
                self.wm.ah.send_commands()

            # only think if new data has arrived
            if self.__should_think_on_data:
                # flag that data has been processed.  this shouldn't be a race
                # condition, since the only change would be to make it True
                # before changing it to False again, and we're already going to
                # process data, so it doesn't make any difference.
                self.__should_think_on_data = False


                # DEBUG:  tells us if a thread dies
                if not self._think_thread.is_alive() or not self._msg_thread.is_alive():
                    raise Exception("A thread died.")

                # performs the actions necessary for the agent to play soccer
                self.think()
            else:
                # prevent from burning up all the cpu time while waiting for data
                time.sleep(0.0001)

    def think(self):
        """
        This method must be overwritten by the Player

        """
        pass

    def initialization(self):
        """
        This method is called just once and before the think loop

        """
        pass
