from smsoccer.players.abstractplayer import AbstractPlayer

class AbstractGoalie(AbstractPlayer):
    """
    AbstractGoalie class

    Has function to help a goalie agent
    """

    def __init__(self):
        super(AbstractGoalie, self).__init__( goalie = True )

    def is_ball_catchable(self):
        #TODO implement this
        pass
