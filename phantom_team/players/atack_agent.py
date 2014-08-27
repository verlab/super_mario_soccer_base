
from smsoccer.players.abstractplayer import AbstractPlayer
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes

class AtackAgent(AbstractPlayer):
    """
    Goalie Agent for Robocup Soccer Team
    """

    def __init__(self):
        super(AtackAgent, self).__init__()

        self._back_to_goal = False
        self._my_goal_position = None

        self.__control_turn = True

    def think(self):
        """
        Think method
        """
        if not self.in_kick_off_formation:

            self._my_goal_position = player_position(self.wm.uniform_number, self.wm.side == WorldModel.SIDE_R)
            # Teleport to right position
            self.wm.teleport_to_point(self._my_goal_position)
            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        if not self.wm.is_before_kick_off():

            if self._back_to_goal:

                if self.__control_turn:
                    self.wm.turn_body_to_point( self._my_goal_position )
                else:
                    self.wm.ah.dash(20)

                if self.wm.get_distance_to_point( self._my_goal_position ) <= 10:
                    self._back_to_goal = False

                self.__control_turn = not self.__control_turn
                return

            if self.wm.ball is None or self.wm.ball.direction is None:
                self.wm.ah.turn(20)
            else:
                if self.wm.is_ball_kickable():
                    self.wm.ah.catch(0)

                    if self.wm.ball is not None:
                        self.wm.kick_to( self.goal_pos )

                        self._back_to_goal = True
                else:
                    self.wm.ah.dash(50)

            if self.wm.get_distance_to_point( self._my_goal_position ) > 25:
                self._back_to_goal = True

