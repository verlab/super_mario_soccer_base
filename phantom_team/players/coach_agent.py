
from smsoccer.players.abstractcoach import AbstractCoach
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes

class CoachAgent(AbstractCoach):
    """
    Goalie Agent for Robocup Soccer Team
    """

    def __init__(self):
      super(CoachAgent, self).__init__()

    def think(self):
        """
        Think method
        """
        pass
