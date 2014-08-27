from smsoccer.players.abstractagent import AbstractAgent


class AbstractCoach(AbstractAgent):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self):
        AbstractAgent.__init__(self, False)

    def initialization(self):
        self.wm.ah.eye_on(True)
        pass

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        pass