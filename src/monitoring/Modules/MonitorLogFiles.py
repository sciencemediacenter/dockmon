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

import datetime
import logging
from Config import _
from monitoring.Modules.MonitorBase import Monitor
from typing import Union, Dict, Any, List


class MonitorLogfile(Monitor):
    def __init__(self, container_name: str, container_labels: Dict[str, Any]):

        self._container_name = container_name
        self._container_labels = container_labels

        # Prepare the Wordlists
        self._includes: List[str] = self._container_labels.get(
            "io.smclab.dockmon.monitoring.logs.include", []
        ).split(",")
        self._excludes: List[str] = self._container_labels.get(
            "io.smclab.dockmon.monitoring.logs.exclude", []
        ).split(",")

        # Check if we should monitor case sensitive or not
        if not self._container_labels.get("io.smclab.dockmon.monitoring.logs.casesensitive", True):
            self._includes = [x.lower() for x in self._includes]
            self._excludes = [x.lower() for x in self._excludes]

        super().__init__(container_name, container_labels)

    def _get_unix_time_stamp_for_interval(self, interval: int) -> int:
        return int((datetime.datetime.today() - datetime.timedelta(seconds=interval)).timestamp())

    def check_config(self) -> bool:
        """This should check if every parameter that is needed to run the monitoring job is set.
        Also if there are any problems with the container itself.

        Returns:
            bool: true, if everything is fine
        """

        # Check all general Parameters
        if not super().check_general_settings():
            return False

        # Check module specific Parameters
        if not super().check_required_parameters(
            [
                "io.smclab.dockmon.monitoring.logs.include",
                "io.smclab.dockmon.monitoring.logs.exclude",
            ]
        ):
            return False

        return True

    def check(self) -> Union[bool, dict]:
        """Checks the occurence of a work in the a part of a logfile.

        Returns:
            Union[bool, dict]: if an alert occures:

                                {
                                    "data": Logfile, which contains the alert
                                    "trigger": Logfile Trigger
                                }

                                else:

                                    False

        """

        if not self._dh.check_container_still_active(self._container_name):
            return False

        if container := self._dh.get_container_obj_by_name(self._container_name):

            # Prepare the logs
            try:
                logs: str = container.logs(
                    since=self._get_unix_time_stamp_for_interval(
                        int(
                            self._container_labels.get(
                                "io.smclab.dockmon.monitoring.logs.since", 60
                            )
                        )
                    )
                ).decode()
            except ValueError:
                logging.error(_("MONITORLOG_EXCEPTION_DECODE"))
                return False

            if not logs:
                return False

            # Check if we should monitor case sensitive or not
            if not self._container_labels.get(
                "io.smclab.dockmon.monitoring.logs.casesensitive", True
            ):
                logs = logs.lower()

            # Check the Log file!
            if any(x in logs for x in self._includes) and not any(
                x in logs for x in self._excludes
            ):
                return {"data": logs, "trigger": _("MONITORLOG_TRIGGER_WORD_INCLUDE")}

        return False
