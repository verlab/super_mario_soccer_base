

def player_position(uniform_number, r_side):
    """
    Defines the formation of each player
    :param uniform_number: number of the player.
    :param r_side: True if team is on right side.
    :return: position based on formation
    """
    # used to flip x coords for other side
    side_mod = 1
    if r_side:
        side_mod = -1

    if uniform_number == 1:
        position = (-5 * side_mod, 30)
    elif uniform_number == 2:
        position = (-40 * side_mod, 15)
    elif uniform_number == 3:
        position = (-40 * side_mod, 00)
    elif uniform_number == 4:
        position = (-40 * side_mod, -15)
    elif uniform_number == 5:
        position = (-5 * side_mod, -30)
    elif uniform_number == 6:
        position = (-20 * side_mod, 20)
    elif uniform_number == 7:
        position = (-20 * side_mod, 0)
    elif uniform_number == 8:
        position = (-20 * side_mod, -20)
    elif uniform_number == 9:
        position = (-10 * side_mod, 0)
    elif uniform_number == 10:
        position = (-10 * side_mod, 20)
    elif uniform_number == 11:
        position = (-10 * side_mod, -20)

    return position