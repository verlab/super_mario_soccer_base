from smsoccer.players.abstractagent import AbstractAgent

class AbstractCoach(AbstractAgent):
    """
    AbstractCoach class

    Has function to help a coach agent
    """

    def __init__(self):
        super(AbstractCoach, self).__init__()

    def initialization(self):
        self.wm.ah.eye_on(True)
        pass

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        pass
