"""
Support for Litter-Robots.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/
"""
import asyncio
from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.discovery import async_load_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .litter_robot import LitterRobot

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'litter_robot'

PLATFORMS = ["sensor"]

SCAN_INTERVAL = timedelta(seconds=120)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=SCAN_INTERVAL
        ): cv.time_period,
    })
}, extra=vol.ALLOW_EXTRA)

SERVICE_NIGHTLIGHT_TURN_ON_SCHEMA = vol.Schema(
    {vol.Optional('litter_robot_id'): cv.string}
)

SERVICE_NIGHTLIGHT_TURN_OFF_SCHEMA = vol.Schema(
    {vol.Optional('litter_robot_id'): cv.string}
)

SERVICE_CYCLE_SCHEMA = vol.Schema(
    {vol.Optional('litter_robot_id'): cv.string}
)

RESET_DRAWER_SCHEMA = vol.Schema(
    {vol.Optional('litter_robot_id'): cv.string}
)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up the Litter-Robot component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    update_interval = conf.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    litter_robot = LitterRobot(username, password)
    coordinator = hass.data[DOMAIN] = LitterRobotDataUpdateCoordinator(
        hass, litter_robot=litter_robot, update_interval=update_interval)
    await coordinator.async_refresh()

    for platform in PLATFORMS:
        hass.async_create_task(async_load_platform(
            hass, platform, DOMAIN, {}, config))

    async def async_nightlight_on_handler(call):
        await litter_robot.async_nightlight_on(call.data or list(litter_robot.robots.keys())[0])
        await asyncio.sleep(15)
        await coordinator.async_request_refresh()

    async def async_nightlight_off_handler(call):
        await litter_robot.async_nightlight_off(call.data or list(litter_robot.robots.keys())[0])
        await asyncio.sleep(15)
        await coordinator.async_request_refresh()

    async def async_cycle_start_handler(call):
        await litter_robot.async_cycle_start(call.data or list(litter_robot.robots.keys())[0])
        await asyncio.sleep(15)
        await coordinator.async_request_refresh()

    async def async_reset_drawer_handler(call):
        await litter_robot.async_reset_drawer(call.data or list(litter_robot.robots.keys())[0])
        await asyncio.sleep(15)
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, 'nightlight_turn_on',
                                 async_nightlight_on_handler, SERVICE_NIGHTLIGHT_TURN_ON_SCHEMA)
    hass.services.async_register(DOMAIN, 'nightlight_turn_off',
                                 async_nightlight_off_handler, SERVICE_NIGHTLIGHT_TURN_OFF_SCHEMA)
    hass.services.async_register(
        DOMAIN, 'cycle', async_cycle_start_handler, SERVICE_CYCLE_SCHEMA)
    hass.services.async_register(
        DOMAIN, 'reset_drawer', async_reset_drawer_handler, RESET_DRAWER_SCHEMA)
    return True


class LitterRobotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching and sending commands to Litter-Robot."""

    def __init__(self, hass, litter_robot, update_interval):
        """Initialize."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=update_interval,
        )
        self.litter_robot = litter_robot

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.litter_robot.async_update()
        except (ConnectionError) as error:
            raise UpdateFailed(error)
        return self.litter_robot.robots
