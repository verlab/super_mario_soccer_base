from smsoccer.players.abstractagent import AbstractAgent
from smsoccer.players.abstractcoach import AbstractCoach


class DemoCoach(AbstractCoach):
    """
    This is a DEMO about how to extend the AbstractAgent and implement the
    think method. For a new development is recommended to do the same.
    """

    def __init__(self):
        AbstractCoach.__init__(self)

    def think(self):
        pass

    def act_in_new_cycle(self):
        if self.wm.ball is not None:
            self._send_world_message()


    def _send_world_message(self):
        # Header: coach world message
        msg = "{i:c"
        # ball
        msg += ",b:" + str([self.wm.ball.distance, self.wm.ball.direction])
        # Player
        team = [[p.distance, p.direction] for p in self.wm.players if p.team == self.wm.team_name]
        msg += ",t=" + str(team)
        opponents = [[p.distance, p.direction] for p in self.wm.players if p.team != self.wm.team_name]
        msg += ",t=" + str(opponents)
        msg += "}"
        msg = msg.replace(' ', '')
        print msg


if __name__ == "__main__":
    import time
    import sys

    a = DemoCoach()
    a.connect('localhost', 6002, 'default')
    a.play()

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print "Exiting."
        sys.exit()