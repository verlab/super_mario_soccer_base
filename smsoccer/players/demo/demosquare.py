import sys
import time
from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractplayer import AbstractPlayer
from smsoccer.strategy.formation import player_position
from smsoccer.util.geometric import angle_between_points, cut_angle
from smsoccer.world.world_model import WorldModel, PlayModes


class DemoSquare(AbstractPlayer):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """


    def __init__(self, goalie=False, visualization=True):

        AbstractAgent.__init__(self, goalie=goalie)

        self.visualization = visualization

        if visualization:
            from smsoccer.util.fielddisplay import FieldDisplay

            self.display = FieldDisplay()

        self.current_time = 0


    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        if self.visualization:
            self.display.clear()

            # draw particles
            if self.wm.filter_robot_loc:
                for p in self.wm.pf.particles:
                    center = p[:2]
                    angle = p[2]
                    color = (200, 0, 0)
                    self.display.draw_particle(center, angle, color)
                self.display.draw_robot(self.wm.pf.abs_coords, self.wm.pf.abs_body_dir, color=(100, 100, 100))

            if self.wm.abs_coords is not None:
                try:
                    self.display.draw_robot(self.wm.abs_coords, self.wm.abs_body_dir)
                except:
                    pass

                    # if self.wm.ball is not None:
                    # self.display.draw_circle(self.wm.get_object_absolute_coords(self.wm.ball), 4)
                    # print self.wm.ball.direction, self.wm.ball.distance
            self.display.show()

        # take places on the field by uniform number
        if not self.in_kick_off_formation:
            position_point = player_position(self.wm.uniform_number)
            # Teleport to right position

            time.sleep(0.1)
            self.teleport_to_point(position_point)

            # turns to attack field
            if self.wm.side == WorldModel.SIDE_R:
                self.turn(180)

            # Player is ready in formation
            self.in_kick_off_formation = True

            return

    def act_in_new_cycle(self):
        # self.wm.abs_coords = self.wm.pf.abs_coords
        # self.wm.abs_body_dir = self.wm.pf.abs_body_dir

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
                            self.dash(50)
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
                self.turn(35)
                return

            # kick it at the enemy goal
            if self.is_ball_kickable():
                try:
                    angle = cut_angle(angle_between_points(self.wm.abs_coords, self.goal_pos)) - cut_angle(
                        self.wm.abs_body_dir)
                    self.wm.ah.kick(20, angle)
                except:
                    print "error in angle to kick"
                    self.wm.ah.kick(2, 0)

                return
            else:
                # move towards ball
                if -7 <= self.wm.ball.direction <= 7:
                    self.dash(5 * self.wm.ball.distance + 20)
                else:
                    # face ball
                    self.turn(self.wm.ball.direction / 2)

                return
