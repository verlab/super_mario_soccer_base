from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractgoalie import AbstractGoalie
from smsoccer.players.abstractplayer import AbstractPlayer
from smsoccer.strategy.formation import player_position
from smsoccer.util.geometric import angle_between_points
from smsoccer.world.world_model import WorldModel, PlayModes


class DemoGoalie(AbstractGoalie):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """


    def __init__(self, visualization=False):

        AbstractAgent.__init__(self, goalie=True)

        self.visualization = visualization
        if visualization:
            from smsoccer.util.fielddisplay import FieldDisplay

            self.display = FieldDisplay()


    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        if self.visualization:
            if self.wm.abs_coords[0] is None:
                return

            self.display.clear()
            self.display.draw_robot(self.wm.abs_coords, self.wm.abs_body_dir)
            if self.wm.ball is not None:
                self.display.draw_circle(self.wm.get_object_absolute_coords(self.wm.ball), 4)
            self.display.show()

        # take places on the field by uniform number
        if not self.in_kick_off_formation:
            position_point = player_position(self.wm.uniform_number)
            # Teleport to right position
            self.teleport_to_point(position_point)

            #turns to attack field
            if self.wm.side == WorldModel.SIDE_R:
                self.wm.ah.turn(180)

            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        # kick off!
        if self.wm.play_mode == PlayModes.BEFORE_KICK_OFF:
            # player 9 takes the kick off
            if self.wm.uniform_number == 9:
                if self.is_ball_kickable():
                    # kick with 100% extra effort at enemy goal
                    self.kick_to(self.goal_pos, 1.0)
                    print self.goal_pos
                else:
                    # move towards ball
                    if self.wm.ball is not None:
                        if self.wm.ball.direction is not None \
                                and -7 <= self.wm.ball.direction <= 7:
                            self.wm.ah.dash(50)
                        else:
                            self.wm.turn_body_to_point((0, 0))

                # turn to ball if we can see it, else face the enemy goal
                if self.wm.ball is not None:
                    self.turn_neck_to_object(self.wm.ball)

                return

        # attack!
        else:
            # find the ball
            if self.wm.ball is None or self.wm.ball.direction is None:
                self.wm.ah.turn(35)
                return

            # kick it at the enemy goal
            if self.is_ball_kickable():
                # self.wm.kick_to(self.goal_pos, 1.0)

                cuts = lambda angle1: angle1 + 360 if angle1 < -180 else angle1
                cut = lambda angle1: angle1 - 360 if angle1 > 180 else cuts(angle1)

                angle = cut(angle_between_points(self.wm.abs_coords, self.goal_pos)) - cut(self.wm.abs_body_dir)

                self.wm.ah.kick(20, angle)
                return
            else:
                # move towards ball
                if -7 <= self.wm.ball.direction <= 7:
                    self.wm.ah.dash(5 * self.wm.ball.distance + 20)
                else:
                    # face ball
                    self.wm.ah.turn(self.wm.ball.direction / 2)

                return