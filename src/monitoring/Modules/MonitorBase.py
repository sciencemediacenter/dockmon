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
from Config import _
from handler.DockerHandler import DockerHandler
from typing import Union, Dict, Any


class Monitor:

    _dh: DockerHandler = DockerHandler.getInstance()

    def __init__(self, container_name: str, container_labels: Dict[str, Any]):
        """Base Class of all Monitoring variants

        Args:
            containerName (str): Container Name
            containerLabels (Dict[str, Any]): Container Labels as Dict
        """
        self._container_name = container_name
        self._container_labels = container_labels

    def check_required_parameters(self, parameters: list) -> bool:
        """Check if all required config parameters are present. Parameters will be supplied by the subclass.

        Args:
            _parameters (list): List of Parameters which are required

        Returns:
            bool: true, if everything is okay
        """
        for p in parameters:
            if not p in self._container_labels.keys():
                logging.error(_("MONITORBASE_EXCEPTION_PARAMETER_NOT_FOUND %s") % p)
                logging.error(_("MONITORBASE_EXCEPTION_LIST_PARAMETERS %s") % ", ".join(parameters))
                return False

        return True

    def check_general_settings(self):
        """This checks if all needed general configurations for monitoring are accessable and set

        Returns:
            _type_: true, if everything is okay
        """
        if not self._dh.get_container_obj_by_name(self._container_name):
            logging.error(_("MONITORBASE_EXCEPTION_CONTAINER_NOT_FOUND %s") % self._container_name)
            return False

        return True

    def check_config(self) -> bool:
        """This should check if every parameter that is needed to run the monitoring job is set.
        Also if there are any problems with the container itself.

        Raises:
            NotImplementedError: Needs to be implemented in the subclass

        Returns:
            bool:
        """
        raise NotImplementedError

    def check(self) -> Union[bool, dict]:
        """The actual monitoring function which should be implemented as a background interval job

        Raises:
            NotImplementedError: Needs to be implemented in the subclass

        Returns:
            Union[bool, dict]: {
                                    "data": Data that caused the alert,
                                    "trigger": Description of the alert
                                }
        """
        raise NotImplementedError
