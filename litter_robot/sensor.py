"""
Litter-Robot platform that has supported sensors.
For more details about this platform, please refer to the documentation
https://home-assistant.io/components/
"""

import logging
from homeassistant.helpers.entity import Entity

DEPENDENCIES = ['litter_robot']

LITTER_ROBOT_DOMAIN = 'litter_robot'
LITTER_ROBOT_LOGIN = 'litter_robot_login'
LITTER_ROBOTS = 'litter_robots'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Litter-Robot sensors."""
    controller = hass.data[LITTER_ROBOT_DOMAIN][LITTER_ROBOT_LOGIN]

    devices = []
    for robot in hass.data[LITTER_ROBOT_DOMAIN][LITTER_ROBOTS]:
        devices.append(StatusSensor(robot, controller))
        devices.append(WasteGaugeSensor(robot, controller))

    add_devices(devices, True)


class StatusSensor(Entity):
    """Representation of the status sensor."""

    def __init__(self, robot, controller):
        """Initialize of the sensor."""
        self._robot = robot
        self._controller = controller

    @property
    def icon(self):
        return 'mdi:flash'

    @property
    def name(self):
        """Return the state of the sensor."""
        return 'Litter-Robot Status'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._robot['unitStatus']

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return 'STATE'

    def update(self):
        """Update the state from the sensor."""
        robots = self._controller.update_robots()
        if robots is not None:
            self._robot = robots[0]


class WasteGaugeSensor(Entity):
    """Representation of the cycle sensor."""

    def __init__(self, robot, controller):
        """Initialize of the sensor."""
        self._robot = robot
        self._controller = controller

    @property
    def icon(self):
        return 'mdi:gauge'

    @property
    def name(self):
        """Return the state of the sensor."""
        return 'Litter-Robot Waste'

    @property
    def state(self):
        """Return the state of the sensor."""
        return int(100 * float(self._robot['cycleCount']) / float(self._robot['cycleCapacity']))

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return '%'

    def update(self):
        """Update the state from the sensor."""
        robots = self._controller.update_robots()
        if robots is not None:
            self._robot = robots[0]
