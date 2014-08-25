formation_442 = [None,
                 (-50, 0),      # 1 - GK
                 (-40, 10),     # 2 - CB (left)
                 (-40, -10),    # 3 - CB (right)
                 (-38, 30),     # LB
                 (-38, -30),    # RB
                 (-20, 10),     # CM(left)
                 (-20, -10),    # CM(right)
                 (-18, 20),     # RM
                 (-18, -20),    # LM
                 (-8, 10),      # CF (left)
                 (-8, -10)]     # CF (right)

formation_433 = [None,
                 (-50, 0),      # 1 - GK
                 (-40, 10),     # 2 - CB (left)
                 (-40, -10),    # 3 - CB (right)
                 (-38, 30),     # LB
                 (-38, -30),    # RB
                 (-30, 5),      # DM(left)
                 (-25, -7),     # DM(right)
                 (-20, 3),     # OM
                 (-10, -15),    # LW
                 (-8, 0),      # CF
                 (-10, 15)]    # RW


def player_position(uniform_number, r_side, formation='442'):
    """
    Defines the formation of each player
    :param uniform_number: number of the player.
    :param r_side: True if team is on right side.
    :return: position based on formation
    """

<<<<<<< .merge_file_DLsC7E
    formation_array = formation_442 if formation == '442' else formation_433
    position = formation_array[uniform_number]
=======
    # if r_side:
    #     # used to flip x coords for other side
    #     position = (-position[0], position[1])
>>>>>>> .merge_file_xhZQQK

    '''
    #BUGFIX: flipping is not needed
    if r_side:
        # used to flip coords for other side.
        position = (position[0], position[1])
    '''
    return position