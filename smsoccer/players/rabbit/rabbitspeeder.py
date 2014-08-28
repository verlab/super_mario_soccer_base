import copy
import  smsoccer.strategy.formation as formation
from collections import namedtuple
from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractplayer import AbstractPlayer
from smsoccer.util.geometric import angle_between_points
from smsoccer.world.world_model import WorldModel, PlayModes


class RabbitSpeeder(AbstractPlayer):
    """
    This is the Rabbit line player
    """


    def __init__(self, goalie=False, visualization=False, formation = '002'):

        AbstractAgent.__init__(self, goalie=goalie)

        #tells if last time ball was seen it was at the left of the player (helps in turning)
        self.last_seen_ball = namedtuple('ball', 'direction')
        self.last_seen_ball.direction = 0
        self.formation = formation
        self.visualization = visualization

        if visualization:
            from smsoccer.util.fielddisplay import FieldDisplay

            self.display = FieldDisplay()

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        self.update_visualization()

        #no need to call 'perceive' actions, these are done in abstract agent

        #print [str(p) for p in self.wm.players_persistent['foes'].values() if p.uniform_number is not None]

        self.act()

        self.post_process()

    def act(self):

        if self.wm.is_kick_off():
            self.kick_off_action()
            return

        elif self.wm.play_mode == PlayModes.PLAY_ON:
            self.play_on_action()
            return

    """
    Reacts to a kick off
    """
    def kick_off_action(self):
        #print 'kick_off_action'
        # take places on the field by uniform number
        if not self.in_kick_off_formation:
            position_point = formation.player_position(self.wm.uniform_number)
            #print 'our KO?', self.wm.is_kick_off_us()
            if self.wm.is_kick_off_us() and self.am_i_kicker():
                position_point = (-0.3, 0)

            # Teleport to position
            print 'Teleporting to:', position_point
            self.teleport_to_point(position_point)

            #turns to attack field
            if self.wm.side == WorldModel.SIDE_R:
                self.wm.ah.turn(180)

            # Player is ready in formation
            self.in_kick_off_formation = True
            return

        # kick off!
        if self.wm.is_kick_off_us(): #self.wm.play_mode == PlayModes.BEFORE_KICK_OFF:
            #print 'We will kick off.'

            # most forward player kicks off
            if self.am_i_kicker():#self.wm.uniform_number == 9:
                #print "I'm the kicker!"

                if self.is_ball_kickable():
                    #print 'kicking!'
                    # kick with 100% extra effort at enemy goal
                    self.kick_to(self.goal_pos, 1.0)
                    #print self.goal_pos
                else:
                    #self.teleport_to_point((-1, 0))
                    #print 'teleporting to ball!!'
                    #return
                    # move towards ball
                    if self.wm.ball is not None:
                        if self.wm.ball.direction is not None \
                                and -7 <= self.wm.ball.direction <= 7:
                            self.wm.ah.dash(50)
                        else:
                            pass
                            #self.wm.turn_body_to_point((0, 0)) << ERROR

                # turn to ball if we can see it, else face the enemy goal
                if self.wm.ball is not None:
                    pass#print 'turning neck!'
                    #self.turn_neck_to_object(self.wm.ball)
                return

    def play_on_action(self):
        #print 'play_on_action'

        self.in_kick_off_formation = False

        # find the ball
        if self.wm.ball is None or self.wm.ball.direction is None:
            angle = 35 if self.last_seen_ball and self.last_seen_ball.direction < 0 else -35
            self.wm.ah.turn(angle)
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

    def post_process(self):
        #updates last seen ball direction
        if self.wm.ball is not None and self.wm.ball.direction is not None:
            #print self.last_seen_ball.direction, self.wm.ball.direction
            del self.last_seen_ball
            self.last_seen_ball = self.wm.ball
            #self.last_ball_left = self.wm.ball.direction < 0
                    #and -7 <= self.wm.ball.direction <= 7:

    def am_i_kicker(self):
        """
        Returns whether this player is the official kick-starter of the team
        :return:
        """
        my_position = formation.player_position(self.wm.uniform_number)
        x_positions = [formation.player_position(i)[0] for i in range(1, 12)]  # range: [1,2,...,11]
        return my_position[0] == max([x_pos for x_pos in x_positions])

    def update_visualization(self):
        if self.visualization:
            if self.wm.abs_coords[0] is None:
                return

            self.display.clear()
            self.display.draw_robot(self.wm.abs_coords, self.wm.abs_body_dir)
            if self.wm.ball is not None:
                self.display.draw_circle(self.wm.get_object_absolute_coords(self.wm.ball), 4)
                # print self.wm.ball.direction, self.wm.ball.distance
            self.display.show()