import math
from smsoccer.world.world_model import WorldModel
from smsoccer.world.parameters import ServerParameters
from smsoccer.util.geometric import euclidean_distance, angle_between_points
import time
from smsoccer.world.game_object import Flag
class PlayerActions:
    """
    This file implements the collection of action
    """
    def __init__(self, world_model):
        self.wm = world_model
        self.check = False
        self.goto_option = 0
        self.goto_ki = 0
        self.goto_kp = 10

        self.turn_kp = 0.4
        self.turn_ki = 0.1

    def goto_distance(self, distance):
        pdpower = distance*self.goto_kp + self.wm.speed_amount*self.goto_ki
        self.wm.ah.dash(pdpower)

    def turnto(self, direction):
        turn_power = direction*self.turn_kp - self.wm.speed_direction*self.turn_ki
        self.wm.ah.turn(turn_power)

    def goto_position2(self, point):
        """
            goto position
        """
        distance = euclidean_distance(self.wm.abs_coords, point)
        direction = angle_between_points(self.wm.abs_coords, point)

        if direction > 180:
            direction = direction - 360

        if distance < 1:
            return

        if math.fabs(direction) < 4 or self.goto_option == 0:
            self.goto_distance(distance)
            self.goto_option = 1
        else:
            self.turnto(direction)
            self.goto_option = 0

    def goto_position(self, point, desired_speed):
        """
            goto position, given a specific point on the map and speed
        """
        #TODO: create a PID controller for the player goto

        # how far are we from the desired point?
        point_dist = euclidean_distance(self.wm.abs_coords, point)

        # get absolute direction to the point
        abs_point_dir = angle_between_points(self.wm.abs_coords, point)

        # Put this direction in 360 degrees
        if abs_point_dir > 180:
            abs_point_dir -= 360

        # get relative direction to point from body
        if self.wm.abs_body_dir is not None:
            rel_point_dir = self.wm.abs_body_dir - abs_point_dir
        else:
            rel_point_dir = None

        #info_list = ["rel_point_dir:", int(rel_point_dir), "abs_body_dir",
        #             int(self.wm.abs_body_dir), "abs_point_dir:", int(abs_point_dir),  "distance:", int(point_dist)]
        #print('\t'.join(map(str, info_list)))

        if rel_point_dir is None or -7 <= rel_point_dir <= 7 or \
                rel_point_dir <= 360 and rel_point_dir >= 350 or \
                rel_point_dir >= 0 and rel_point_dir <= 10:
            #calculate the force for the running
            difference_speed = math.fabs(desired_speed - self.wm.speed_amount)

            #calculate edp Documentation 4.5.2
            #edp = self.wm.server_parameters.dash_power_rate*self.wm.effort*difference_speed
            self.wm.ah.dash(difference_speed)
        else:
            if rel_point_dir > 0:
                self.wm.ah.turn(-3)
            else:
                self.wm.ah.turn(3)

    def goalie_wait_in_penalty_area(self, goalieradius, ball_direction):
        # define the field side and the points related to the goal
        if self.wm.side == WorldModel.SIDE_L:
            p1coord = Flag.FLAG_COORDS['glt']
            p2coord = Flag.FLAG_COORDS['glb']
            goalcentercoord = Flag.FLAG_COORDS['gl']
        else:
            p1coord = Flag.FLAG_COORDS['grt']
            p2coord = Flag.FLAG_COORDS['grb']
            goalcentercoord = Flag.FLAG_COORDS['gr']

        #define the center of the circle
        radius = euclidean_distance(p1coord, goalcentercoord)
        #h = math.cos(60)*radius
        #circle_center = (0, 0)
        #define cicle center
        #if self.wm.side == WorldModel.SIDE_L:
        #    circle_center = (goalcentercoord[0] + h, goalcentercoord[1])
        #else:
        #    circle_center = (goalcentercoord[0] - h, goalcentercoord[1] )
        #ball position

        ball_abs_direction = self.wm.abs_body_dir + ball_direction

        radius = max(goalieradius, radius)
        ball_dx = radius*math.cos(math.radians(ball_abs_direction))
        ball_dy = radius*math.sin(math.radians(ball_abs_direction))

        player_position = (goalcentercoord[0] + ball_dx, ball_dy + goalcentercoord[1])
        #mylist = ["rel_point_dir:", player_position]
        #print mylist
        #player_position = (circle_center[0] + radius + 10, 0)
        return player_position
        #self.goto_position2((-40, 8))


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



