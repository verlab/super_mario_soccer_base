from smsoccer.players.abstractplayer import AbstractPlayer

class AbstractGoalie(AbstractPlayer):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self):
        super(AbstractGoalie, self).__init__( goalie = True )

    def is_ball_catchable(self):
        #TODO implement this
        pass


