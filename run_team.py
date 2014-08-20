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


import time

from smsoccer.agent import Agent

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

    def spawn_agent(team_name):
        """
        Used to run an agent in a separate physical process.
        """
        try:
            a = Agent()
            a.connect("localhost", 6000, team_name)
            a.play()

            # we wait until we're killed
            while 1:
                # we sleep for a good while since we can only exit if terminated.
                time.sleep(1)

        except:
            print sys.exc_info()[0]

    # spawn all agents as separate processes for maximum processing efficiency
    agent_threads = []
    for agent in xrange(min(11, int(sys.argv[2]))):
        print "  Spawning agent %d..." % agent

        at = mp.Process(target=spawn_agent, args=(sys.argv[1],))
        at.daemon = True
        at.start()

        agent_threads.append(at)

    print "Spawned %d agents." % len(agent_threads)
    print
    print "Playing soccer..."

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
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