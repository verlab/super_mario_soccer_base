
from smsoccer.players.abstractgoalie import AbstractGoalie
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes
from smsoccer.players.playeractions import PlayerActions
from smsoccer.world.game_object import Flag
from smsoccer.players.playeractions import PlayerActions
from smsoccer.util.geometric import euclidean_distance, angle_between_points

class GoalKeeper(AbstractGoalie):
    """
    This file implements the goalkeeper
    """

    def __init__(self, visualization=True):

        AbstractGoalie.__init__(self)
        self.player_actions = None

        self.visualization = visualization
        if visualization:
            from smsoccer.util.fielddisplay import FieldDisplay
            self.display = FieldDisplay()
        self.last_ball_direction = 0
        self.player_last_position = (0, 0)

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        if self.player_actions is None:
            self.player_actions = PlayerActions(self.wm)

        if self.visualization:
            if self.wm is None or self.wm.abs_coords is None:
                return

            self.display.clear()
            self.display.draw_robot(self.wm.abs_coords, self.wm.abs_body_dir)
            if self.wm.ball is not None:
                self.display.draw_circle(self.wm.get_object_absolute_coords(self.wm.ball), 4)
                # print self.wm.ball.direction, self.wm.ball.distance
            self.display.show()

        # take places on the field by uniform number
        if not self.in_kick_off_formation:
            position_point = Flag.FLAG_COORDS['gl']
            # Teleport to right position
            self.teleport_to_point((position_point[0], position_point[1]))
            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        if self.wm.play_mode == PlayModes.KICK_OFF_L or self.wm.play_mode == PlayModes.PLAY_ON:
            if self.wm.ball is not None:
                #calculates the next position
                player_pos = self.player_actions.goalie_wait_in_penalty_area(0, self.wm.ball.direction)
                #calculate the distance to desired point
                player_pos_distance = euclidean_distance(player_pos, self.wm.abs_coords)

                #save current variables
                self.player_last_position = player_pos
                self.last_ball_direction = self.wm.ball.direction
                if player_pos_distance > 3:
                    #if the distance is higher than 3, go to position
                    self.player_actions.goto_position(player_pos, 60)
                else:
                    #The player know will turn to ball direction
                    if self.last_ball_direction < -5:
                        self.wm.ah.turn(-5)
                    if self.last_ball_direction > 5:
                        self.wm.ah.turn(5)
            else:

                player_pos_distance = euclidean_distance(self.player_last_position, self.wm.abs_coords)
                #
                if player_pos_distance > 4:
                     #if the distance is higher than 4, go to position
                    self.player_actions.goto_position(self.player_last_position, 60)
                else:
                    #The player know will turn to ball direction
                    if self.last_ball_direction < -5:
                        self.wm.ah.turn(-5)
                    if self.last_ball_direction > 5:
                        self.wm.ah.turn(5)



        self.display.draw_circle(self.player_last_position, 4)

        self.display.show()