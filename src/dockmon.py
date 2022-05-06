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

import logging
import os
import sys
import time
from Config import _, _REQUIRED_ENV
from handler.DockerHandler import DockerHandler
from monitoring.MonitorScheduler import MonitorScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ],
)


if __name__ == "__main__":
    logging.info(_("INIT_CORE_STARTUP"))

    # Try to get access to the docker daemon
    _dh = DockerHandler.getInstance()
    if not _dh.check_connection():
        sys.exit(1)

    # Check the Config.
    if not all(item in os.environ and item for item in _REQUIRED_ENV):
        logging.info(_("INIT_CONFIG_MISSING_ENVIRONMENT_VARS"))
        sys.exit(1)

    # Check the Scheduler
    _scheduler = MonitorScheduler.getInstance()
    _scheduler.init_monitoring_threads()

    # Starting the Main loop
    try:
        while _scheduler.check_scheduler_status():
            time.sleep(60 * 1)
        logging.error(_("CORE_SCHEDULER_NOT_RUNNING_EXIT"))
        sys.exit(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Exiting")
