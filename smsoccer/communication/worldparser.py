from smsoccer.world import game_object
from smsoccer.world.world_model import WorldModel


def parse_message_see(msg, wm):
    # store new values before changing those in the world model.  all new
    # values replace those in the world model at the end of parsing.
    new_ball = None
    new_flags = []
    new_goals = []
    new_lines = []
    new_players = []
    sim_time = msg[1]

    # iterate over all the objects given to us in the last see message
    for obj in msg[2:]:
        name = obj[0]
        members = obj[1:]

        # get basic information from the object.  different numbers of
        # parameters (inconveniently) specify different types and
        # arrangements of data received for the object.

        # default values for object data
        distance = None
        direction = None
        dist_change = None
        dir_change = None
        body_dir = None
        neck_dir = None

        # a single item object means only direction
        if len(members) == 1:
            direction = members[0]

        # objects with more items follow a regular pattern
        elif len(members) >= 2:
            distance = members[0]
            direction = members[1]

            # include delta values if present
            if len(members) >= 4:
                dist_change = members[2]
                dir_change = members[3]

            # include body/neck values if present
            if len(members) >= 6:
                body_dir = members[4]
                neck_dir = members[5]

        # parse flags
        if name[0] == 'f':
            # since the flag's name sometimes contains a number, the parser
            # recognizes it as such and converts it into an int.  it's
            # always the last item when it's a number, so we stringify the
            # last item of the name to convert any numbers back.
            name[-1] = str(name[-1])

            # the flag's id is its name's members following the f as a string
            flag_id = ''.join(name[1:])

            new_flags.append(game_object.Flag(distance, direction, flag_id))

        # parse players
        elif name[0] == 'p':
            # extract any available information from the player object's name
            team_name = None
            uniform_number = None

            if len(name) >= 2:
                team_name = name[1]
            if len(name) >= 3:
                uniform_number = name[2]
            if len(name) >= 4:
                position = name[3]

            # figure out the player's side
            side = None
            if team_name is not None:
                # if they're on our team, they're on our side
                if team_name == wm.team_name:
                    side = wm.side
                # otherwise, set side to the other team's side
                else:
                    if wm.side == WorldModel.SIDE_L:
                        side = WorldModel.SIDE_R
                    else:
                        side = WorldModel.SIDE_L

            # calculate player's speed
            speed = None
            # TODO: calculate player's speed!

            new_players.append(game_object.Player(distance, direction,
                                                  dist_change, dir_change, speed, team_name, side,
                                                  uniform_number, body_dir, neck_dir))

        # parse goals
        elif name[0] == 'g':
            # see if we know which side's goal this is
            goal_id = None
            if len(name) > 1:
                goal_id = name[1]

            new_goals.append(game_object.Goal(distance, direction, goal_id))

        # parse lines
        elif name[0] == 'l':
            # see if we know which line this is
            line_id = None
            if len(name) > 1:
                line_id = name[1]

            new_lines.append(game_object.Line(distance, direction, line_id))

        # parse the ball
        elif name[0] == 'b':
            # TODO: handle speed!
            new_ball = game_object.Ball(distance, direction, dist_change,
                                        dir_change, None)

        # object very near to but not viewable by the player are 'blank'

        # the out-of-view ball
        elif name[0] == 'B':
            new_ball = game_object.Ball(None, None, None, None, None)

        # an out-of-view flag
        elif name[0] == 'F':
            new_flags.append(game_object.Flag(None, None, None))

        # an out-of-view goal
        elif name[0] == 'G':
            new_goals.append(game_object.Goal(None, None, None))

        # an out-of-view player
        elif name[0] == 'P':
            new_players.append(game_object.Player(None, None, None, None,
                                                  None, None, None, None, None, None))

        # an unhandled object type
        else:
            raise Exception("Unknown object: '" + str(obj) + "'")


    return new_ball, new_flags, new_goals, new_players, new_lines, sim_time