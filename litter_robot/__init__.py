"""
Support for Litter-Robots.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/
"""
import logging
from datetime import timedelta
import requests

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_X_API_KEY = 'api_key'

DOMAIN = 'litter_robot'
DEPENDENCIES = []

LITTER_ROBOT_LOGIN = 'litter_robot_login'
LITTER_ROBOTS = 'litter_robots'

ATTR_CYCLE_COUNT = 'cycleCount'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_X_API_KEY): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Litter-Robot component."""

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][LITTER_ROBOT_LOGIN] = LitterRobotHub(
        hass, config[DOMAIN], LitterRobotConnection)
    hub = hass.data[DOMAIN][LITTER_ROBOT_LOGIN]
    if not hub.login():
        _LOGGER.info("Failed to login to Litter-Robot API")
        return False
    hub.update_robots()
    discovery.load_platform(hass, 'sensor', DOMAIN, {}, config)
    
    return True


class LitterRobotConnection:

    def __init__(self, username, password, x_api_key):
        self._username = username
        self._password = password
        self._x_api_key = x_api_key

    def login(self):
        response = requests.post('https://muvnkjeut7.execute-api.us-east-1.amazonaws.com/staging/login', json={
            'email': self._username, "oneSignalPlayerId": "0", "password": self._password}, headers={'x-api-key': self._x_api_key})
        response_json = response.json()
        self._auth_token = response_json['token']
        self._user_id = response_json['user']['userId']

    def robots(self):
        response = requests.get('https://muvnkjeut7.execute-api.us-east-1.amazonaws.com/staging/users/' + self._user_id +
                                '/litter-robots', headers={'x-api-key': self._x_api_key, 'Authorization': self._auth_token})
        response_json = response.json()
        return response_json

    def dispatch_command(self, robot_id, command):
        requests.post('https://muvnkjeut7.execute-api.us-east-1.amazonaws.com/staging/users/' + self._user_id + '/litter-robots/' + robot_id + '/dispatch-commands', json={
                                'command': command, 'litterRobotId': robot_id }, headers={'x-api-key': self._x_api_key, 'Authorization': self._auth_token})


class LitterRobotHub:
    """A My Litter-Robot hub wrapper class."""

    def __init__(self, hass, domain_config, litter_robot_connection):
        """Initialize the Litter-Robot hub."""
        self.config = domain_config
        self._hass = hass
        my_litter_robots = litter_robot_connection(
            self.config[CONF_USERNAME], self.config[CONF_PASSWORD], self.config[CONF_X_API_KEY])
        self._my_litter_robots = my_litter_robots

        def handle_nightlight_turn_on(call):
            try:
                robot_id = hass.data[DOMAIN][LITTER_ROBOTS][0]['litterRobotId']
                my_litter_robots.dispatch_command(robot_id, '<N1')
                hass.data[DOMAIN][LITTER_ROBOTS][0]['nightLightActive'] = '1'
            except:
                _LOGGER.error("Unable to send <N1 command to Litter-Robot API")
        
        def handle_nightlight_turn_off(call):
            try:
                robot_id = hass.data[DOMAIN][LITTER_ROBOTS][0]['litterRobotId']
                my_litter_robots.dispatch_command(robot_id, '<N0')
                hass.data[DOMAIN][LITTER_ROBOTS][0]['nightLightActive'] = '0'
            except:
                _LOGGER.error("Unable to send <N0 command to Litter-Robot API")

        def handle_cycle(call):
            try:
                robot_id = hass.data[DOMAIN][LITTER_ROBOTS][0]['litterRobotId']
                my_litter_robots.dispatch_command(robot_id, '<C')
            except:
                _LOGGER.error("Unable to send <C command to Litter-Robot API")

        hass.services.register(DOMAIN, 'nightlight_turn_on', handle_nightlight_turn_on)
        hass.services.register(DOMAIN, 'nightlight_turn_off', handle_nightlight_turn_off)
        hass.services.register(DOMAIN, 'cycle', handle_cycle)

    def login(self):
        """Login to My Litter-Robot."""
        try:
            _LOGGER.info("Trying to connect to Litter-Robot API")
            self._my_litter_robots.login()
            return True
        except:
            _LOGGER.error("Unable to connect to Litter-Robot API")
            return False

    @Throttle(timedelta(seconds=300))
    def update_robots(self):
        """Update the robot states."""
        self._hass.data[DOMAIN][LITTER_ROBOTS] = self._my_litter_robots.robots()
        return self._hass.data[DOMAIN][LITTER_ROBOTS]
