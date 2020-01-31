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
LITTER_ROBOT_UNIT_STATUS = {
  'RDY': 'Ready',
  'CCP': 'Clean Cycling',
  'CCC': 'Ready - Clean Cycling Complete',
  'DF1': 'Ready - 2 Cycles Until Full',
  'DF2': 'Ready - 1 Cycle Until Full',
  'CSI': 'Cat Sensor Interrupt',
  'CST': 'Cat Sensor Timing',
  'BR' : 'Bonnet Removed',
  'P'  : 'Paused',
  'OFF': 'Off',
  'SDF': 'Not Ready - Drawer Full',
  'DFS': 'Not Ready - Drawer Full',
  'CSF': 'Cat Sensor Interrupted'
}
SENSOR_PREFIX = 'Litter-Robot '

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Litter-Robot sensors."""
    controller = hass.data[LITTER_ROBOT_DOMAIN][LITTER_ROBOT_LOGIN]

    devices = []
    for robot in hass.data[LITTER_ROBOT_DOMAIN][LITTER_ROBOTS]:
        devices.append(StatusSensor(robot, controller))
        devices.append(WasteGaugeSensor(robot, controller))
        devices.append(NightLightStatusSensor(robot, controller))

    add_devices(devices, True)


class StatusSensor(Entity):
    """Representation of the status sensor."""

    def __init__(self, robot, controller):
        """Initialize of the sensor."""
        self._robot = robot
        self._controller = controller
        self._name = SENSOR_PREFIX + robot['litterRobotNickname'] + ' status'

    @property
    def icon(self):
        return 'mdi:flash'

    @property
    def name(self):
        """Return the state of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return information about the device."""
        return {
            "litter_robot_id": self._robot['litterRobotId']
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        sleep_mode_active = self._robot['sleepModeActive']
        unit_status = self._robot['unitStatus']
        if sleep_mode_active != '0' and unit_status == 'RDY':
            # over 8 hours since last sleep 
            if int(sleep_mode_active[1:].split(':')[0]) < 8:
                return 'Sleeping'
        
        return LITTER_ROBOT_UNIT_STATUS.get(unit_status, unit_status)

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return None

    def update(self):
        """Update the state from the sensor."""
        robots = self._controller.update_robots()
        if robots is not None:
            self._robot = [x for x in robots if x['litterRobotId'] == self._robot['litterRobotId']][0]


class WasteGaugeSensor(Entity):
    """Representation of the cycle sensor."""

    def __init__(self, robot, controller):
        """Initialize of the sensor."""
        self._robot = robot
        self._controller = controller
        self._name = SENSOR_PREFIX + robot['litterRobotNickname'] + ' waste'

    @property
    def icon(self):
        return 'mdi:gauge'

    @property
    def name(self):
        """Return the state of the sensor."""
        return self._name

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
            self._robot = [x for x in robots if x['litterRobotId'] == self._robot['litterRobotId']][0]

class NightLightStatusSensor(Entity):
    """Representation of the night light status sensor."""

    def __init__(self, robot, controller):
        """Initialize of the sensor."""
        self._robot = robot
        self._controller = controller
        self._name = SENSOR_PREFIX + robot['litterRobotNickname'] + ' nightlight'

    @property
    def icon(self):
        return 'mdi:lightbulb-on' if self.state == 'On' else 'mdi:lightbulb'

    @property
    def name(self):
        """Return the state of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return 'On' if self._robot['nightLightActive'] != '0' else 'Off'

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return None

    def update(self):
        """Update the state from the sensor."""
        robots = self._controller.update_robots()
        if robots is not None:
            self._robot = [x for x in robots if x['litterRobotId'] == self._robot['litterRobotId']][0]
