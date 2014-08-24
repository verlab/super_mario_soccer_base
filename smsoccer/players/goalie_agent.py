
from smsoccer.abstractagent import AbstractAgent
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes


class GoalieAgent(AbstractAgent):
    """
    Goalie Agent for Robocup Soccer Team
    """

    def __init__(self):
        AbstractAgent.__init__(self, goalie=True)

    def think(self):
        """
        Think method
        """
        if not self.in_kick_off_formation:
            position_point = player_position(self.wm.uniform_number, self.wm.side == WorldModel.SIDE_R)
            # Teleport to right position
            self.wm.teleport_to_point(position_point)
            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        if not self.wm.is_before_kick_off():
            if self.wm.ball is None or self.wm.ball.direction is None:
                self.wm.ah.turn(20)
            else:
                self.wm.ah.catch(0)
