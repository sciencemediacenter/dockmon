"""
    This File is part of DockMon - See README for further information.
    Copyright (C) 2020  Hendrik Adam <hendrik.adam@sciencemediacenter.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import gettext
import sys
import os
from typing import List

###
#   Translation
###
translate = gettext.translation("messages", sys.path[0] + "/locale", languages=["en_US"])
_ = translate.gettext

###
# Reporting
###

# Alerting Colors
ALERT_LEVEL_LOW = "#26FA00"
ALERT_LEVEL_MEDIUM = "#EBFA00"
ALERT_LEVEL_HIGH = "#ED2525"

###
# Envrionment Vars
###
_REQUIRED_ENV: List[str] = [
    "DOCKMON_CONFIG_GRACEPERIOD",
    "DOCKMON_CONFIG_SLACK_TOKEN",
    "DOCKMON_CONFIG_SLACK_CHANNEL",
]
DOCKMON_CONFIG_GRACEPERIOD = os.environ.get("DOCKMON_CONFIG_GRACEPERIOD", 3600)
DOCKMON_CONFIG_SLACK_TOKEN = os.environ.get("DOCKMON_CONFIG_SLACK_TOKEN", "")
DOCKMON_CONFIG_SLACK_CHANNEL = os.environ.get("DOCKMON_CONFIG_SLACK_CHANNEL", "")
