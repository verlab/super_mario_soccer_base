
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
        pass
