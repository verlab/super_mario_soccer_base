from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractcoach import AbstractCoach


class DemoCoach(AbstractCoach):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self):
        AbstractAgent.__init__(self, False)

    def think(self):
        pass






if __name__ == "__main__":
    import time
    import sys

    a = AbstractCoach()
    a.connect('localhost', 6002, 'default')
    a.play()

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print "Exiting."
        sys.exit()