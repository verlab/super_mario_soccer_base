#!/usr/bin/env python

import time
import sys

from soccerpy.agent import Agent

PORT = 6000

HOST = "localhost"

"""
Run an agent
"""
if __name__ == "__main__":
    # enforce current number of arguments, print help otherwise
    if len(sys.argv) == 3:
        print "args: ./run_team.py <team_name> <num_players>"
        #Get team name from arguments
        team_name = sys.argv[1]
    else:
        team_name = "default"

    a = Agent()
    a.connect(HOST, PORT, team_name)
    a.play()



    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print "Exiting."
        sys.exit()

