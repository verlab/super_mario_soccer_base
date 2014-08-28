from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractcoach import AbstractCoach


class RabbitMaster(AbstractCoach):
    """
    RabbitMaster is the legendary rabbit coach
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