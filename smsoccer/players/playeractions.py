import math
from smsoccer.world.world_model import WorldModel
from smsoccer.world.parameters import ServerParameters
from smsoccer.util.geometric import euclidean_distance, angle_between_points
import time

class PlayerActions:
    """
    This file implements the collection of action
    """
    def __init__(self, world_model):
        self.wm = world_model

    def goto_position(self, point, desired_speed):
        """
            goto position, given a specific point on the map and speed
        """
        #TODO: create a PID controller for the player goto

        #print "GOTO_POS called"
        # how far are we from the desired point?
        point_dist = euclidean_distance(self.wm.abs_coords, point)

        # get absolute direction to the point
        abs_point_dir = angle_between_points(self.wm.abs_coords, point)


        if self.wm.abs_body_dir:
            if self.wm.abs_body_dir < 0:
                self.wm.abs_body_dir += 360

        # get relative direction to point from body, since kicks are relative to
        # body direction.
        if self.wm.abs_body_dir is not None:
            rel_point_dir = self.wm.abs_body_dir - abs_point_dir
        else:
            rel_point_dir = None

        #print "rel_point_dir:", int(rel_point_dir), "abs_body_dir", int(self.wm.abs_body_dir), \
        #    "abs_point_dir:", int(abs_point_dir), "point_dist", int(point_dist), "abs_coords", self.wm.abs_coords

        mylist = ["rel_point_dir:", int(rel_point_dir), "abs_body_dir", int(self.wm.abs_body_dir), "abs_point_dir:", int(abs_point_dir)]
        print('\t'.join(map(str,mylist)))


        #self.wm.ah.turn(1)

        if rel_point_dir is None or -10 <= rel_point_dir <= 10:
            #calculate the force for the running
            difference_speed = math.fabs(desired_speed - self.wm.speed_amount)

            #calculate edp Documentation 4.5.2
            #edp = self.wm.server_parameters.dash_power_rate*self.wm.effort*difference_speed
            self.wm.ah.dash(difference_speed)
        else:
            # face the point
            self.wm.ah.turn(5)

            #self.wm.ah.turn(5)
            #time.sleep(0.5)

    '''
    def goalie_wait_in_penalty_area(self, ball):
        # define the field side and the points related to the goal
        if self.wm.side == WorldModel.SIDE_L:
            p1coord = self.wm.flag_dict['glt']
            p2coord = self.wm.flag_dict['glb']
            goalcentercoord =  self.wm.flag_dict['gl']
        else:
            p1coord = self.wm.flag_dict['grt']
            p2coord = self.wm.flag_dict['grb']
            goalcentercoord = self.wm.flag_dict['glr']

        #define the center of the circle
        radius = euclidean_distance(p1coord, p2coord)
        h = math.cos(60)*radius
        #define cicle center
        if self.wm.side == WorldModel.SIDE_L:
            circlecenter[0] = goalcentercoord[0]
            circlecenter[1] = goalcentercoord[1] - h
        else
            circlecenter[0] = goalcentercoord[0]
            circlecenter[1] = goalcentercoord[1] + h

        dx = math.cos(ball.direction)*radius
        dy = math.sin(ball.direction)*radius

        playerposition[0] = circlecenter[0] + dx
        playerposition[1] = circlecenter[1] + dy
        #send position message
    '''

    '''
        if -10 <= 360 - abs_point_dir <= 10:
            #calculate the force for the running
            #difference_speed = desired_speed - self.wm.speed_amount

            #given the the speed calculate the dash power
            #dash_power = difference_speed

            #calculate edp Documentation 4.5.2
            #edp = self.wm.server_parameters.dash_power_rate*self.wm.effort*power
            self.wm.ah.dash(20)
        else:
            # face the point
            if not -180 <= rel_point_dir <= 180:
                if rel_point_dir < -180:
                    rel_point_dir = -180
                else:
                    rel_point_dir = 180

            self.wm.ah.turn(rel_point_dir)

            #self.wm.ah.turn(5)
            #time.sleep(1)
    '''



