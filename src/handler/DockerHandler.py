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

import docker
import logging
from Config import _
from typing import Dict, Any


class DockerHandler:
    """
    The DockerHandler creates an abstraction layer for the necessary tasks related to Docker.
    """

    _instance = None

    @staticmethod
    def getInstance(storageConnector=None):
        if DockerHandler._instance == None:
            DockerHandler()
            return DockerHandler._instance
        else:
            return DockerHandler._instance

    # Allows this class to be pickled by APScheduler - Thanks: https://github.com/agronholm/apscheduler/issues/421
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_client"]  # remove the unpicklable DockerClient
        return state

    # will be called on unpickling
    def __setstate__(self, state):
        self.__dict__.update(state)
        try:
            self._client: docker.DockerClient = docker.DockerClient(
                base_url="unix://var/run/docker.sock"
            )
        except Exception as e:
            self._client: None = None
            logging.error(_("DOCKERHANDLER_EXCEPTION_SOCKET_CONNECT" % str(e)))

    def __init__(self):
        if DockerHandler._instance != None:
            raise Exception("Singleton!")
        else:
            try:
                self._client: docker.DockerClient = docker.DockerClient(
                    base_url="unix://var/run/docker.sock"
                )
            except Exception as e:
                self._client: None = None
                logging.error(_("DOCKERHANDLER_EXCEPTION_SOCKET_CONNECT" % str(e)))

            DockerHandler._instance = self

    def check_connection(self) -> bool:
        """Test the connection to the Docker Socket

        Returns:
            bool: True, if connection is ok
        """
        if not self._client:
            logging.error(_("DOCKERHANDLER_EXCEPTION_DOCKERCLIENT_NONE"))
            return False

        try:
            self._client.info()
        except docker.errors.APIError:
            logging.error(_("DOCKERHANDLER_EXCEPTION_API_ERROR"))
            return False

        logging.info(_("DOCKERHANDLER_SOCKET_CONNECTION_ACCEPTED"))
        return True

    def get_docker_handle(self) -> docker.DockerClient:
        """Returns the Docker Client handle

        Returns:
            docker.DockerClient: Current Docker Client Handle
        """
        return self._client

    def get_container_obj_by_name(self, container_name: str) -> docker.models.containers.Container:
        """Returns the corresponding Docker Containter Object by Name

        Args:
            container_name (str): Name of the Container or ID

        Returns:
            docker.models.containers.Container: Docker Container Object
        """
        try:
            return self._client.containers.get(container_name)
        except docker.errors.NotFound:
            logging.error(_("DOCKERHANDLER_EXCEPTION_CONTAINER_NOT_FOUND"))
            return None

    def check_container_still_active(self, container_name: str) -> bool:
        """Checks if a Container is still alive (= Status 'runnung')

        Args:
            container_name (str): Container Name or ID

        Returns:
            bool: True, if Container is still running
        """
        try:
            container: docker.models.containers.Container = self._client.containers.get(
                container_name
            )
        except docker.errors.NotFound:
            return False

        if container.status == "running":
            return True

        return False

    def get_containers_for_monitoring(self) -> Dict[str, Dict[str, Any]]:
        """Discovers all Containers with the Label io.smclab.dockmon.enabled = true.
        It will return a Dict with the Containername (or ID, if no name is provided) as key, and a Dict with all
        relevant Labels for Dockmon.

        Returns:
            Dict[str, Dict[str, Any]]: Dict containing all Containers with corresponding labels.
        """

        containers: Dict[str, Dict[str, Any]] = {}
        for container in self._client.containers.list(
            filters={"label": ["io.smclab.dockmon.enabled=True"], "status": "running"}
        ):
            container_name = container.name or container.id
            containers[container_name] = container.labels

        return containers
