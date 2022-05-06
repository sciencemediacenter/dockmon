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
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler
from Config import _
from handler.DockerHandler import DockerHandler
from handler.SlackReporting import SlackReport
from monitoring.Modules.MonitorLogFiles import MonitorLogfile


class MonitorScheduler:
    """
    Schedule all Monitoring Jobs and provide an interface to them.

    Basically, all monitoring tasks are outsourced to individual threads, which in turn return their results to this class via callbacks.
    The "discovery thread" takes on the additional role of discovering new Docker containers and configuring them for monitoring
    """

    _instance = None
    _scheduler: BackgroundScheduler
    _slack: SlackReport = SlackReport.getInstance()
    _docker: DockerHandler = DockerHandler.getInstance()

    @staticmethod
    def getInstance():
        if MonitorScheduler._instance == None:
            MonitorScheduler()
            return MonitorScheduler._instance
        else:
            return MonitorScheduler._instance

    def __init__(self):
        if MonitorScheduler._instance != None:
            raise Exception("Singleton!")
        else:

            # Clear JobStorage on Startup
            try:
                os.remove(sys.path[0] + "/MonitoringJobs.sqlite")
            except FileNotFoundError:
                pass

            self._scheduler = BackgroundScheduler(
                {
                    "apscheduler.jobstores.default": {
                        "type": "sqlalchemy",
                        "url": "sqlite:///" + sys.path[0] + "/MonitoringJobs.sqlite",
                    },
                    "apscheduler.executors.default": {
                        "class": "apscheduler.executors.pool:ThreadPoolExecutor",
                        "max_workers": "30",
                    },
                    "apscheduler.executors.processpool": {
                        "type": "processpool",
                        "max_workers": "5",
                    },
                    "apscheduler.job_defaults.coalesce": "true",
                    "apscheduler.job_defaults.max_instances": "3",
                    "apscheduler.timezone": "UTC",
                }
            )

            # Remove APScheduler INFO Logs, only log on WARNING or ERROR
            logging.getLogger("apscheduler").setLevel(logging.WARNING)

            try:
                self._scheduler.start()
            except Exception as e:
                logging.error(_("MONITORSCHEDULER_EXECPTION_SCHEDULER_NOT_STARTED %s") % str(e))
            MonitorScheduler._instance = self

    def _handle_discovery_return_event(self, event: JobExecutionEvent):
        """Handles the returned Data from the Discovery-Thread.

        Args:
            event (JobExecutionEvent): The event-data from the apscheduler. Contains everything we need to know
        """

        # We know that the discovery event.retval is a Dict - So we iterate over it to configure monitoring jobs.
        for container_name, labels in event.retval.items():

            # Check for Logfile Monitoring
            if labels.get("io.smclab.dockmon.monitoring.logs", False):

                _mon = MonitorLogfile(container_name, labels)
                if _mon.check_config() and not self._scheduler.get_job(container_name):
                    self._scheduler.add_job(
                        _mon.check,
                        trigger="interval",
                        seconds=labels.get("io.smclab.dockmon.monitoring.checkinterval", 60),
                        id=container_name,
                    )
                    logging.info(
                        _("MONITORSCHEDULER_ADDED_SCHEDULER_THREAD %s %d")
                        % (
                            container_name,
                            labels.get("io.smclab.dockmon.monitoring.checkinterval", 60),
                        )
                    )

    def _monitoring_job_return_listener(self, event: JobExecutionEvent):
        """APscheduler Return Listener. Will be executed when a Job is executed and returns data

        Args:
            event (JobExecutionEvent): return values and event data of the returning job

        """
        if event.exception:
            logging.error(_("MONITORSCHEDULER_EXCEPTION_THREAD_EXCEPTION %s") % event.job_id)
            logging.error("Traceback %s" % event.traceback)
        else:

            # Check, which thread has returned. Please APSchduler, provide the possibility to set individual listener for jobs..

            # ... Discovery ?
            if event.job_id == "dockmon_discovery":
                self._handle_discovery_return_event(event)

            # ... actual Monitoring Event ?
            else:
                # A Monitor reported a true value!
                if event.retval:
                    logging.info(_("MONITORSCHEDULER_ALERT_TRIGGER %s") % event.job_id)
                    self._slack.send_slack_info_report(
                        event.job_id,
                        event.retval.get("trigger", ""),
                        event.retval.get("data", ""),
                    )

    def check_scheduler_status(self) -> bool:
        """Checks the if the scheduler is still running. Also, maybe even more important, checks if all running jobs still
        have their corresponding containers. If a Container does disappear, this function will remove the job from the scheduler.

        Returns:
            bool: True, if the scheduler is running
        """

        # Check if all Monitoring Jobs have corresponding containers
        for job in self._scheduler.get_jobs():
            if not job.id == "dockmon_discovery" and not self._docker.check_container_still_active(
                job.id
            ):
                self._scheduler.remove_job(job.id)
                logging.info(_("MONITORSCHEDULER_REMOVE_JOB_MISSING_CONTAINER %s" % job.id))

        return self._scheduler.running

    def init_monitoring_threads(self):
        """Registers the Return Listener and starts the Container Discovery-Thread"""
        logging.info(_("MONITORSCHEDULER_INIT"))

        # Add the Event Listener to get the Return Values of the Monitoring Jobs
        self._scheduler.add_listener(
            self._monitoring_job_return_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        # Starting Discovery Thread
        self._scheduler.add_job(
            self._docker.get_containers_for_monitoring,
            trigger="interval",
            seconds=10,
            id="dockmon_discovery",
        )
        logging.info(_("MONITORSCHEDULER_STARTED_DISCOVERY_THREAD"))
