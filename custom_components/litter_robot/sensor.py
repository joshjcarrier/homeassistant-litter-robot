"""
Litter-Robot platform that has supported sensors.
For more details about this platform, please refer to the documentation
https://home-assistant.io/components/
"""

import logging

from homeassistant.helpers.entity import Entity

from . import DOMAIN

LITTER_ROBOT_UNIT_STATUS = {
    'RDY': 'Ready',
    'CCP': 'Clean Cycling',
    'CCC': 'Ready - Clean Cycling Complete',
    'DF1': 'Ready - 2 Cycles Until Full',
    'DF2': 'Ready - 1 Cycle Until Full',
    'CSI': 'Cat Sensor Interrupt',
    'CST': 'Cat Sensor Timing',
    'BR': 'Bonnet Removed',
    'P': 'Paused',
    'OFF': 'Off',
    'SDF': 'Not Ready - Drawer Full',
    'DFS': 'Not Ready - Drawer Full',
    'CSF': 'Cat Sensor Interrupted'
}
SENSOR_PREFIX = 'Litter-Robot '

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    """Add Brother entities from a config_entry."""
    coordinator = hass.data[DOMAIN]

    sensors = []
    for id in coordinator.data:
        device_info = {
            "litter_robot_id": coordinator.data[id]['litterRobotId']
        }
        sensors.append(StatusSensor(coordinator, id, device_info))
        sensors.append(WasteGaugeSensor(coordinator, id, device_info))
        sensors.append(NightLightStatusSensor(coordinator, id, device_info))

    async_add_entities(sensors, False)


class LitterRobotEntity(Entity):
    def __init__(self, coordinator, id, device_info):
        """Initialize of the entity."""
        self.coordinator = coordinator
        self._id = id
        self._device_info = device_info

    @property
    def device_state_attributes(self):
        """Return the device_info of the device."""
        return self._device_info

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Disconnect from update signal."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    def _robot(self):
        return self.coordinator.data[self._id]


class StatusSensor(LitterRobotEntity):
    """Representation of the status sensor."""

    def __init__(self, coordinator, id, device_info):
        """Initialize of the sensor."""
        LitterRobotEntity.__init__(self, coordinator, id, device_info)
        self._name = SENSOR_PREFIX + \
            coordinator.data[id]['litterRobotNickname'] + ' status'

    @property
    def icon(self):
        return 'mdi:flash'

    @property
    def name(self):
        """Return the state of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        robot = self._robot()
        sleep_mode_active = robot['sleepModeActive']
        unit_status = robot['unitStatus']
        if sleep_mode_active != '0' and unit_status == 'RDY':
            # over 8 hours since last sleep
            if int(sleep_mode_active[1:].split(':')[0]) < 8:
                return 'Sleeping'

        return LITTER_ROBOT_UNIT_STATUS.get(unit_status, unit_status)

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return None


class WasteGaugeSensor(LitterRobotEntity):
    """Representation of the cycle sensor."""

    def __init__(self, coordinator, id, device_info):
        """Initialize of the sensor."""
        LitterRobotEntity.__init__(self, coordinator, id, device_info)
        self._name = SENSOR_PREFIX + \
            coordinator.data[id]['litterRobotNickname'] + ' waste'

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
        robot = self._robot()
        return int(100 * float(robot['cycleCount']) / float(robot['cycleCapacity']))

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return '%'


class NightLightStatusSensor(LitterRobotEntity):
    """Representation of the night light status sensor."""

    def __init__(self, coordinator, id, device_info):
        """Initialize of the sensor."""
        LitterRobotEntity.__init__(self, coordinator, id, device_info)
        self._name = SENSOR_PREFIX + \
            coordinator.data[id]['litterRobotNickname'] + ' nightlight'

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
        robot = self._robot()
        return 'On' if robot['nightLightActive'] == '1' else 'Off'

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return None
