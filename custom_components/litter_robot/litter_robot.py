import aiohttp
import jwt
import logging

_LOGGER = logging.getLogger(__name__)

X_API_KEY = 'p7ndMoj61npRZP5CVz9v4Uj0bG769xy6758QRBPb'


class LitterRobot:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self.robots = {}
        self._auth_token = None
        self._user_id = None

    async def async_update(self):
        try:
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots',
                                       headers={'x-api-key': X_API_KEY, 'Authorization': self._auth_token}) as r:
                    if r.status >= 300:
                        _LOGGER.error("[update] Unexpected response: %s", r)
                    json_body = await r.json()
                    for robot in json_body:
                        self.robots[robot["litterRobotId"]] = robot
        except Exception as ex:
            _LOGGER.error("[update] Unexpected exception: %s", ex)

    async def async_nightlight_on(self, robot_id):
        await self.async_send_command(robot_id, '<N1')

    async def async_nightlight_off(self, robot_id):
        await self.async_send_command(robot_id, '<N0')

    async def async_cycle_start(self, robot_id):
        await self.async_send_command(robot_id, '<C')

    async def async_reset_drawer(self, robot_id):
        try:
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                async with session.patch('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots/' + robot_id,
                                         json={'cycleCount': '0',
                                               'cycleCapacity': '46', 'cyclesAfterDrawerFull': '0'},
                                         headers={'x-api-key': X_API_KEY, 'Authorization': self._auth_token}) as r:
                    if r.status >= 300:
                        _LOGGER.error(
                            "[reset drawer] Unexpected response: %s", r)
        except Exception as ex:
            _LOGGER.error("[reset drawer] Unexpected exception: %s", ex)

    async def async_send_command(self, robot_id, command):
        try:
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                async with session.post('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots/' + robot_id + '/dispatch-commands',
                                        json={'command': command,
                                              'litterRobotId': robot_id},
                                        headers={'x-api-key': X_API_KEY, 'Authorization': self._auth_token}) as r:
                    if r.status >= 300:
                        _LOGGER.error(
                            "[command %s] Unexpected response: %s", command, r)
        except Exception as ex:
            _LOGGER.error("[command %s] Unexpected exception: %s", command, ex)

    async def _async_login(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://autopets.sso.iothings.site/oauth/token',
                                        data={
                                            'client_id': 'IYXzWN908psOm7sNpe4G.ios.whisker.robots',
                                            'client_secret': 'C63CLXOmwNaqLTB2xXo6QIWGwwBamcPuaul',
                                            'grant_type': 'password',
                                            'username': self._username,
                                            "password": self._password}) as r:
                    if r.status >= 300:
                        _LOGGER.error("[login] Unexpected response: %s", r)
                        return
                    response_json = await r.json()
                    self._auth_token = response_json['access_token']
                    claims = jwt.decode(
                        response_json['access_token'], verify=False)
                    self._user_id = claims.get('userId')
        except Exception as ex:
            _LOGGER.error("[login] Unexpected exception: %s", ex)
