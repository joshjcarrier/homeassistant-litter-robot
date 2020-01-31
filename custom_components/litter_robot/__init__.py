"""
Support for Litter-Robots.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/
"""
import logging
from datetime import timedelta
import jwt
import requests

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'litter_robot'
DEPENDENCIES = []

LITTER_ROBOT_LOGIN = 'litter_robot_login'
LITTER_ROBOTS = 'litter_robots'

ATTR_CYCLE_COUNT = 'cycleCount'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
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

def setup(hass, config):
    """Set up the Litter-Robot component."""

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][LITTER_ROBOT_LOGIN] = LitterRobotHub(
        hass, config[DOMAIN], LitterRobotConnection)
    hub = hass.data[DOMAIN][LITTER_ROBOT_LOGIN]
    if not hub.login():
        _LOGGER.error("Failed to login to Litter-Robot API")
        return False
    hub.update_robots()
    discovery.load_platform(hass, 'sensor', DOMAIN, {}, config)
    
    return True


class LitterRobotConnection:

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._x_api_key = 'p7ndMoj61npRZP5CVz9v4Uj0bG769xy6758QRBPb'

    def login(self):
        response = requests.post('https://autopets.sso.iothings.site/oauth/token', data={
            'client_id': 'IYXzWN908psOm7sNpe4G.ios.whisker.robots',
            'client_secret': 'C63CLXOmwNaqLTB2xXo6QIWGwwBamcPuaul',
            'grant_type': 'password',
            'username': self._username, 
            "password": self._password
            })
        response_json = response.json()
        self._auth_token = response_json['access_token']
        claims = jwt.decode(response_json['access_token'], verify=False)
        self._user_id = claims.get('userId')

    def robots(self):
        self.login()
        response = requests.get('https://v2.api.whisker.iothings.site/users/' + self._user_id +
                                '/robots', headers={'x-api-key': self._x_api_key, 'Authorization': self._auth_token})
        response_json = response.json()
        return response_json

    def dispatch_command(self, robot_id, command):
        self.login()
        response = requests.post('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots/' + robot_id + '/dispatch-commands', json={
                                'command': command, 'litterRobotId': robot_id }, headers={'x-api-key': self._x_api_key, 'Authorization': self._auth_token})

class LitterRobotHub:
    """A My Litter-Robot hub wrapper class."""

    def __init__(self, hass, domain_config, litter_robot_connection):
        """Initialize the Litter-Robot hub."""
        self.config = domain_config
        self._hass = hass
        my_litter_robots = litter_robot_connection(
            self.config[CONF_USERNAME], self.config[CONF_PASSWORD])
        self._my_litter_robots = my_litter_robots

        def get_litter_robot_id(self, call_data):
            litter_robot_id = call_data.get('litter_robot_id', None)
            if litter_robot_id is not None:
                return [x for x in self._hass.data[DOMAIN][LITTER_ROBOTS] if x['litterRobotId'] == litter_robot_id][0]['litterRobotId']
            return self._hass.data[DOMAIN][LITTER_ROBOTS][0]['litterRobotId']

        def set_litter_robot_state(self, litter_robot_id, key, value):
            [x for x in self._hass.data[DOMAIN][LITTER_ROBOTS] if x['litterRobotId'] == litter_robot_id][0][key] = value

        def handle_nightlight_turn_on(call):
            try:
                robot_id = get_litter_robot_id(self, call.data)
                my_litter_robots.dispatch_command(robot_id, '<N1')
                set_litter_robot_state(self, robot_id, 'nightLightActive', '1')
            except Exception as ex:
                _LOGGER.error("Unable to send <N1 command to Litter-Robot API %s", ex)
        
        def handle_nightlight_turn_off(call):
            try:
                robot_id = get_litter_robot_id(self, call.data)
                my_litter_robots.dispatch_command(robot_id, '<N0')
                set_litter_robot_state(self, robot_id, 'nightLightActive', '0')
            except Exception as ex:
                _LOGGER.error("Unable to send <N0 command to Litter-Robot API %s", ex)

        def handle_cycle(call):
            try:
                robot_id = get_litter_robot_id(self, call.data)
                my_litter_robots.dispatch_command(robot_id, '<C')
            except Exception as ex:
                _LOGGER.error("Unable to send <C command to Litter-Robot API %s", ex)

        hass.services.register(DOMAIN, 'nightlight_turn_on', handle_nightlight_turn_on, SERVICE_NIGHTLIGHT_TURN_ON_SCHEMA)
        hass.services.register(DOMAIN, 'nightlight_turn_off', handle_nightlight_turn_off, SERVICE_NIGHTLIGHT_TURN_OFF_SCHEMA)
        hass.services.register(DOMAIN, 'cycle', handle_cycle, SERVICE_CYCLE_SCHEMA)

    def login(self):
        """Login to My Litter-Robot."""
        try:
            _LOGGER.info("Trying to connect to Litter-Robot API")
            self._my_litter_robots.login()
            return True
        except:
            _LOGGER.error("Unable to connect to Litter-Robot API")
            return False

    @Throttle(timedelta(seconds=120))
    def update_robots(self):
        """Update the robot states."""
        self._hass.data[DOMAIN][LITTER_ROBOTS] = self._my_litter_robots.robots()
        return self._hass.data[DOMAIN][LITTER_ROBOTS]
