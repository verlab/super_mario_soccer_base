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

formation_002 = [None,
                 (-50, 0),      # 1 - GK
                 (-8, 8),       # CF
                 (-8, -8),      #CF -- below are just to avoid errors if rabbit is called with 11 players
                 (-40, 10),     # 2 - CB (left)
                 (-40, -10),    # 3 - CB (right)
                 (-38, 30),     # LB
                 (-38, -30),    # RB
                 (-20, 10),     # CM(left)
                 (-20, -10),    # CM(right)
                 (-18, 20),     # RM
                 (-18, -20)]    # LM



def player_position(uniform_number, formation='002'):
    """
    Defines the formation of each player
    :param formation:
    :param uniform_number: number of the player.
    :return: position based on formation
    """

    if formation == '002':
        formation_array = formation_002
    elif formation == '442':
        formation_array = formation_442
    else:
        formation_array = formation_433

    position = formation_array[uniform_number]

    return position