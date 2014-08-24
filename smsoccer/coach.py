from smsoccer.abstractagent import AbstractAgent


class Coach(AbstractAgent):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self):
        AbstractAgent.__init__(self, False)

    def initialization(self):
        # TODO eye on
        pass

    def think(self):
        """
        Performs a single step of thinking for our agent.  Gets called on every
        iteration of our think loop.
        """
        ah = self.wm.ah
        self.wm.ah.eye_on(True)


        # TODO choose the best players

        # TODO put the formation



if __name__ == "__main__":
    import time
    import sys

    a = Coach()
    a.connect('localhost', 6002, 'default')
    a.play()

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print "Exiting."
        sys.exit()