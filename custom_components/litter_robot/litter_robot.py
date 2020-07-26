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
        async def async_run():
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots',
                                       headers={'x-api-key': X_API_KEY,
                                                'Authorization': self._auth_token},
                                       raise_for_status=True) as r:
                    json_body = await r.json()
                    for robot in json_body:
                        self.robots[robot["litterRobotId"]] = robot
        try:
            await async_run()
        except Exception as ex:
            _LOGGER.error("[update] Unexpected exception: %s", ex)
            self._logout()
            await async_run()

    async def async_nightlight_on(self, robot_id):
        await self.async_send_command(robot_id, '<N1')

    async def async_nightlight_off(self, robot_id):
        await self.async_send_command(robot_id, '<N0')

    async def async_cycle_start(self, robot_id):
        await self.async_send_command(robot_id, '<C')

    async def async_sleep_enable(self, robot_id, hours, minutes, seconds):
        await self.async_send_command(robot_id, '<S1{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds))

    async def async_sleep_disable(self, robot_id):
        await self.async_send_command(robot_id, '<S0')

    async def async_reset_drawer(self, robot_id):
        async def async_run():
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                await session.patch('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots/' + robot_id,
                                    json={'cycleCount': '0',
                                          'cycleCapacity': '46', 'cyclesAfterDrawerFull': '0'},
                                    headers={'x-api-key': X_API_KEY,
                                             'Authorization': self._auth_token},
                                    raise_for_status=True)
        try:
            await async_run()
        except Exception as ex:
            _LOGGER.error("[reset drawer] Unexpected exception: %s", ex)
            self._logout()
            await async_run()

    async def async_send_command(self, robot_id, command):
        async def async_run():
            await self._async_login()
            async with aiohttp.ClientSession() as session:
                await session.post('https://v2.api.whisker.iothings.site/users/' + self._user_id + '/robots/' + robot_id + '/dispatch-commands',
                                   json={'command': command,
                                         'litterRobotId': robot_id},
                                   headers={'x-api-key': X_API_KEY,
                                            'Authorization': self._auth_token},
                                   raise_for_status=True)
        try:
            await async_run()
        except Exception as ex:
            _LOGGER.error("[command %s] Unexpected exception: %s", command, ex)
            self._logout()
            await async_run()

    async def _async_login(self):
        if self._auth_token is not None:
            try:
                jwt.decode(self._auth_token,
                           options={'verify_signature': False, 'verify_exp': True})
                _LOGGER.info("[login] Reusing valid auth token")
                return
            except Exception as ex:
                _LOGGER.info("[login] Auth token is no longer valid: %s", ex)
                self._logout()

        async def async_run():
            async with aiohttp.ClientSession() as session:
                async with session.post('https://autopets.sso.iothings.site/oauth/token',
                                        data={
                                            'client_id': 'IYXzWN908psOm7sNpe4G.ios.whisker.robots',
                                            'client_secret': 'C63CLXOmwNaqLTB2xXo6QIWGwwBamcPuaul',
                                            'grant_type': 'password',
                                            'username': self._username,
                                            "password": self._password},
                                        raise_for_status=True) as r:
                    response_json = await r.json()
                    self._auth_token = response_json['access_token']
                    claims = jwt.decode(
                        response_json['access_token'], verify=False)
                    self._user_id = claims.get('userId')
        try:
            await async_run()
        except Exception as ex:
            _LOGGER.error("[login] Unexpected exception: %s", ex)
            self._logout()
            await async_run()

    def _logout(self):
        self._auth_token = None
        self._user_id = None
