#!/usr/bin/env python

# ----------------------------------------------------------------------------
# GNU General Public License v2
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ----------------------------------------------------------------------------


from time import sleep

from smsoccer.players.demo.democoach import DemoCoach
from smsoccer.players.demo.demogoalie import DemoGoalie
from smsoccer.players.demo.demoplayer import DemoPlayer


PORT_PLAYERS = 6000
PORT_COACH = 6002


def spawn_coach(team_name):
    """
    Used to run an agent in a separate physical process.
    """
    try:
        a = DemoCoach()
        a.connect("localhost", PORT_COACH, team_name)
        a.play()

        # we wait until we're killed
        while 1:
            # we sleep for a good while since we can only exit if terminated.
            sleep(1)
    except:
        print sys.exc_info()[0]


def spawn_agent(team_name, goalie):
    """
    Used to run an agent in a separate physical process.
    """
    try:

        a = DemoGoalie() if goalie else DemoPlayer()
        a.connect("localhost", PORT_PLAYERS, team_name)
        a.play()

        # we wait until we're killed
        while 1:
            # we sleep for a good while since we can only exit if terminated.
            sleep(1)
    except:
        print sys.exc_info()[0]


"""
Run N players in different threads.
"""
if __name__ == "__main__":
    import sys
    import multiprocessing as mp

    # enforce current number of arguments, print help otherwise
    if len(sys.argv) < 3:
        print "args: ./run_team.py <team_name> <num_players>"
        sys.exit()

    # spawn all agents as separate processes for maximum processing efficiency
    agent_threads = []

    # Goalie
    print "  Spawning goalie"
    ag = mp.Process(target=spawn_agent, args=(sys.argv[1], True))
    ag.daemon = True
    ag.start()
    agent_threads.append(ag)
    sleep(0.1)

    # # Spawn players
    for agent in xrange(min(10, int(sys.argv[2]) - 1)):
        print "  Spawning agent %d..." % agent
        at = mp.Process(target=spawn_agent, args=(sys.argv[1], False))
        at.daemon = True
        at.start()
        agent_threads.append(at)

    # Coach
    print "  Spawning coach"
    ac = mp.Process(target=spawn_coach, args=(sys.argv[1],))
    ac.daemon = True
    ac.start()
    agent_threads.append(ac)

    print "RUN SUPER MARIO!!"

    # wait until killed to terminate agent processes
    try:
        while 1:
            sleep(0.05)
    except KeyboardInterrupt:
        print
        print "Killing agent threads..."

        # terminate all agent processes
        count = 0
        for at in agent_threads:
            print "  Terminating agent %d..." % count
            at.terminate()
            count += 1
        print "Killed %d agent threads." % (count - 1)

        print
        print "Exiting."
        sys.exit()