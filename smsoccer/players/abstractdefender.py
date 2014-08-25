
from smsoccer.abstractagent import AbstractAgent
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel, PlayModes


class AbstractDefender(AbstractAgent):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self, goalie=False):
        AbstractAgent.__init__(self, goalie=goalie)

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """

        # take places on the field by uniform number
        if not self.in_kick_off_formation:
            position_point = player_position(self.wm.uniform_number, self.wm.side == WorldModel.SIDE_R)
            # Teleport to right position
            self.wm.teleport_to_point(position_point)
            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        # kick off!
        if self.wm.play_mode == PlayModes.BEFORE_KICK_OFF:
            # player 9 takes the kick off
            if self.wm.uniform_number == 9:
                if self.wm.is_ball_kickable():
                    # kick with 100% extra effort at enemy goal
                    self.wm.kick_to(self.goal_pos, 1.0)
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
                    self.wm.turn_neck_to_object(self.wm.ball)

                return

        # attack!
        else:
            # find the ball
            if self.wm.ball is None or self.wm.ball.direction is None:
                self.wm.ah.turn(30)

                return

            # kick it at the enemy goal
            if self.wm.is_ball_kickable():
                self.wm.kick_to(self.goal_pos, 1.0)
                return
            else:
                # move towards ball
                if -7 <= self.wm.ball.direction <= 7:
                    self.wm.ah.dash(65)
                else:
                    # face ball
                    self.wm.ah.turn(self.wm.ball.direction / 2)

                return
