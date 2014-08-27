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
import sys

from players.goalie_agent import GoalieAgent

PORT = 6000

HOST = "localhost"

"""
Run an agent
"""
if __name__ == "__main__":
    # enforce current number of arguments, print help otherwise

    if len(sys.argv) == 2:
        print "args: ./run_team.py <team_name>"
        #Get team name from arguments
        team_name = sys.argv[1]
    else:
        team_name = "default"

    GoalieAgent().connect(HOST, PORT, team_name).play()

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print "Exiting."
        sys.exit()

