formation_442 = [None,
                 (-50, 0),  # 1
                 (-40, 10),  # 2
                 (-40, -10),  # 3
                 (-38, 30),
                 (-38, -30),
                 (-20, 10),  # 6
                 (-20, -10),  # 3
                 (-18, 20),
                 (-18, -20),
                 (-8, 10),
                 (-8, -10)]


def player_position(uniform_number, r_side):
    """
    Defines the formation of each player
    :param uniform_number: number of the player.
    :param r_side: True if team is on right side.
    :return: position based on formation
    """
    position = formation_442[uniform_number]

    # if r_side:
    #     # used to flip x coords for other side
    #     position = (-position[0], position[1])

    return position