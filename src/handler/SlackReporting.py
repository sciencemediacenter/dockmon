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
import json
import logging
import os
import requests
from Config import (
    _,
    DOCKMON_CONFIG_GRACEPERIOD,
    DOCKMON_CONFIG_SLACK_CHANNEL,
    DOCKMON_CONFIG_SLACK_TOKEN,
)

# from dotenv import load_dotenv
# load_dotenv()


class SlackReport:
    """
    Automated Slack reporting.
    """

    _instance = None
    _grace_periods: list = []

    @staticmethod
    def getInstance():
        if SlackReport._instance == None:
            SlackReport()
            return SlackReport._instance
        else:
            return SlackReport._instance

    def __init__(self):
        if SlackReport._instance != None:
            raise Exception("Singleton!")
        else:
            SlackReport._instance = self

    def _get_unix_time_stamp_for_grace_period(self) -> int:
        return int(
            (
                datetime.datetime.today()
                + datetime.timedelta(seconds=int(DOCKMON_CONFIG_GRACEPERIOD))
            ).timestamp()
        )

    def send_slack_info_report(self, container: str, trigger: str, report: str) -> bool:
        """Sends the Slack Message

        Args:
            container (str): Container Name / Identifier
            trigger (str): Triggername
            report (str): Report Text
            action (tuple, optional): _description_. Defaults to ("None", "#ED2525").

        Returns:
            bool: True, if report was send successfully
        """

        # Check if this notification is currently under a grace period and should therefore not be triggered again.
        for alert in self._grace_periods:
            if alert.get("container", "") == container and alert.get("trigger", "") == trigger:
                # We found a Grace Period for this Alert. Check if it is expired, if so remove it.
                if alert.get("graceUntil") < int(datetime.datetime.today().timestamp()):
                    self._grace_periods.remove(alert)
                else:
                    # Grace Period is still valid, return
                    logging.info(_("SLACKREPORT_GRACE_PERIOD_NOT_EXPIRED"))
                    return False

        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            data = {
                "token": DOCKMON_CONFIG_SLACK_TOKEN,
                "channel": DOCKMON_CONFIG_SLACK_CHANNEL,
                "attachments": json.dumps(
                    [
                        {
                            "mrkdwn_in": ["text"],
                            "color": "#ED2525",
                            "text": _("SLACKREPORT_TRIGGER_MESSAGE %s") % container,
                            "fields": [
                                {"type": "divider"},
                                {
                                    "title": _("SLACKREPORT_HEADER_TRIGGER"),
                                    "value": trigger,
                                    "short": False,
                                },
                                {
                                    "title": _("SLACKREPORT_HEADER_REPORT"),
                                    "value": "``` %.1500s ```" % report,
                                    "short": False,
                                },
                            ],
                            "footer": "Docker Monitoring",
                            "ts": int((datetime.datetime.today()).timestamp()),
                        }
                    ]
                ),
            }

            res = requests.post(url, data, headers)
            if not res.json().get("ok"):
                logging.error(_("SLACKREPORT_EXCEPTION_API_ERROR %s") % str(res.text))

            # Add Grace Period
            self._grace_periods.append(
                {
                    "container": container,
                    "trigger": trigger,
                    "graceUntil": self._get_unix_time_stamp_for_grace_period(),
                }
            )
            return True
        except Exception as e:
            logging.error(_("SLACKREPORT_EXCEPTION_API_ERROR %s") % str(e))
            return False
