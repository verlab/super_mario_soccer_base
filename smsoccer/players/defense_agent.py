
from smsoccer.abstractagent import AbstractAgent
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes
from smsoccer.util.fielddisplay import FieldDisplay

class DefenseAgent(AbstractAgent):
    """
    Goalie Agent for Robocup Soccer Team
    """

    def __init__(self, visualization=False):
        super(DefenseAgent, self).__init__()

        self.visualization = visualization
        if visualization:
            self.display = FieldDisplay( True )

    def think(self):
        """
        Think method
        """

        if self.visualization:
            if self.wm.abs_coords[0] is None: return

            self.display.clear()
            self.display.draw_robot(self.wm.abs_coords, self.wm.abs_body_dir)

            if self.wm.ball is not None:
                self.display.draw_circle(self.wm.get_object_absolute_coords(self.wm.ball), 4)

            self.display.show()

        if not self.in_kick_off_formation:

            position_point = player_position( self.wm.uniform_number, self.wm.side == WorldModel.SIDE_R )
            # Teleport to right position
            self.wm.teleport_to_point( position_point )
            # Player is ready in formation
            self.in_kick_off_formation = True
            return
