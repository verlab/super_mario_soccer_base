from time import sleep

from smsoccer.abstractagent import AbstractAgent
from smsoccer.communication import action
from smsoccer.strategy.formation import player_position
from smsoccer.world.world_model import WorldModel


class Doidao(AbstractAgent):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self, goalie=False):
        AbstractAgent.__init__(self, goalie=goalie)
        self.current_time = 0

        self.x = []
        self.y = []

        self.setup = False

    def initialization(self):
        r_side = self.wm.side == WorldModel.SIDE_R

        position_point = player_position(self.wm.uniform_number, r_side)

        # Teleport to right position
        self.wm.teleport_to_point(position_point)

        if r_side:
            self.wm.ah.turn(180)

        self.wm.ah.change_view_quality(action.VIEW_WIDTH_NORMAL,
                                       action.VIEW_QUALITY_HIGH)

        sleep(0.5)

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        ah = self.wm.ah

        if self.wm.sim_time == 0:
            return

        new_cycle = self.current_time < self.wm.sim_time

        if not new_cycle:
            return


        # # find the ball
        if self.wm.ball is None or self.wm.ball.direction is None:
            self.wm.ah.turn(55)
            return
        #
        # kick it at the enemy goal
        if self.wm.is_ball_kickable():
            # self.wm.kick_to(self.goal_pos, 1.0)
            ah.kick(20, 0)
            return
        else:
            p = self.wm.ball.distance * 5 + 40
            print p, self.wm.ball.distance, self.wm.ball.speed
            # move towards ball
            if -7 <= self.wm.ball.direction <= 7:
                self.wm.ah.dash(p)
            else:
                # face ball
                self.wm.ah.turn(self.wm.ball.direction / 2)

            return

            # self.x.append(self.wm.abs_coords[0])
            # self.y.append(self.wm.abs_coords[1])
            #
            # npx = np.array(self.x)
            # npy = np.array(self.y)
            #
            # # print self.iter, self.wm.abs_coords, self.wm.abs_neck_dir, self.wm.abs_body_dir
            # # print self.wm.sim_time, (np.mean(npx), np.std(npx)), (np.mean(npy), np.std(npy)), self.wm.abs_coords
            # # self.iter += 1
            # # print self.wm.view_quality, self.wm.view_width
            # print self.wm.abs_coords






            # if self.wm.is_ball_kickable():
            #     # self.wm.kick_to(self.goal_pos, 1.0)
            #     ah.kick(100, 0)
            #
            # else:
            #     ah.dash(40)