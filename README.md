# Litter-Robot

The `litter-robot` component offers integration with the [Litter-Robot](https://www.litter-robot.com/litter-robot-iii-open-air-with-connect.html) WiFi enabled devices to [Home Assistant](https://www.home-assistant.io/).

> 🍻 I'm not employed by Litter Robot, and provide this plugin purely for our own enjoyment.
>
> Use [my referal code](http://share.litter-robot.com/rmc2b) and get \$25 off your own robot (and it tips me too!)

![image](https://user-images.githubusercontent.com/526858/55689115-c8e37780-5935-11e9-979d-298452e87054.png)

## Install

Load this component by copying the custom_components/litter_robot directory and its contents to the custom_components directory in your Home Assistant's configuration directory, typically `/config/custom_components`, but may be [elsewhere](https://www.home-assistant.io/docs/configuration/) depending on your installation. This is easiest with the Samba share add-on.  Alternatively, from a [terminal](https://github.com/home-assistant/addons/blob/master/ssh/DOCS.md) run the following:
```
git clone --depth=1 https://github.com/joshjcarrier/homeassistant-litter-robot.git
cp -r homeassistant-litter-robot/custom_components/litter_robot /config/custom_components/
rm -r homeassistant-litter-robot
```

## Setup

You'll need to have connected to your robot at least once before with the mobile [app](https://www.litter-robot.com/the-app.html).

### Configuration

Edit `/config/configuration.yaml`. For a robot nicknamed "Tesla Meowdel S":

```yaml
litter_robot:
  username: !secret litter_robot_email
  password: !secret litter_robot_password
  scan_interval: 120

switch:
  - platform: template
    switches:
      litter_robot_nightlight:
        friendly_name: "Tesla Meowdel S Night Light"
        value_template: "{{ is_state('sensor.litter_robot_tesla_meowdel_s_nightlight', 'On') }}"
        icon_template: "mdi:lightbulb"
        turn_on:
          service: litter_robot.nightlight_turn_on
        turn_off:
          service: litter_robot.nightlight_turn_off
      litter_robot_cycle:
        friendly_name: "Tesla Meowdel S Cycle"
        value_template: "{{ is_state('sensor.litter_robot_tesla_meowdel_s_status', 'Clean Cycling In Progress') }}"
        icon_template: "mdi:refresh"
        turn_on:
          service: litter_robot.cycle
        turn_off:
      litter_robot_reset_drawer:
        friendly_name: "Tesla Meowdel S Reset Drawer"
        value_template: "{{ is_state('sensor.litter_robot_tesla_meowdel_s_status', 'Clean Cycling In Progress') }}"
        icon_template: "mdi:repeat"
        turn_on:
          service: litter_robot.reset_drawer
        turn_off:
```
Then add the following to your /config/secrets.yaml:
```
litter_robot_email: <your_email@address>
litter_robot_password: <your password>
```
### Finishing setup

Restart HASS to activate the component and to reapply config changes. This can be done from the frontend via Configuration -> General -> Server management -> Restart.

### Troubleshooting

If there's a problem, the new `sensor.litter_robot_*` won't appear. This is most likely invalid configuration (see above) or a Litter Robot username/password problem. Details will be logged in the Developer Tools -> Logs section.

**Password issues:** It's been reported that resetting your Litter Robot account password might help if your password isn't being accepted, so make sure you try updating your mobile app to the latest version and resetting the password!

## Grouping Sensors

Discover the list by searching "litter_robot" in the frontend: Developer tools -> <> (States).

Edit `/config/groups.yaml`. For a robot nicknamed "Tesla Meowdel S":

```yaml
Tesla Meowdel S:
  entities:
    - sensor.litter_robot_tesla_meowdel_s_status
    - sensor.litter_robot_tesla_meowdel_s_error
    - sensor.litter_robot_tesla_meowdel_s_waste
    - switch.litter_robot_cycle
    - switch.litter_robot_nightlight
    - switch.litter_robot_reset_drawer
```

Then reload Groups config. This is easiest done with the frontend Configuration -> General -> Configuration reloading -> Reload groups.

## Multiple robots

The sensors will automatically provision themselves, but to control individual robots you'll need to specify a `data` section in the service call. The `litter_robot_id` should match the Litter Robot API ID and can be found in the Developer Tools -> States tab for the `litter_robot_..._status` sensor.

```yml
turn_on:
  service: litter_robot.nightlight_turn_on
  data:
    litter_robot_id: a00bb111cccca
```

## Development

Watch `/config/home-assistant.log`, which is accessible from the frontend via Developer tools -> (i) (/developer-tools/logs).

### Authentication

`POST https://autopets.sso.iothings.site/oauth/token`

**Security**: none

**Example request body (application/x-www-form-encoded)**:

| Key           | Value                     |
| ------------- | ------------------------- |
| client_id     | \<extracted from iOS app> |
| client_secret | \<extracted from iOS app> |
| grant_type    | password                  |
| username      | \<username, form encoded> |
| password      | \<password, form encoded> |

**Example response body (application/json)**:

```json
{
  "token_type": "Bearer",
  "access_token": "<jwt>",
  "refresh_token": "<refresh token>",
  "expires_in": 3600
}
```

_Decoded JWT_:

```json
{
  "userId": "<user id>",
  ...
}
```

- \<jwt> is used as Authorization header value
- x-api-key is extracted from iOS app

### State

`GET https://v2.api.whisker.iothings.site/users/:user_id/robots`

**Security**: `Authorization`, `x-api-key`

**Example response body**:

```json
[
  {
    "powerStatus": "AC",
    "sleepModeStartTime": "0",
    "lastSeen": "2019-01-01T00:00:00.000000",
    "sleepModeEndTime": "0",
    "autoOfflineDisabled": true,
    "setupDate": "2018-01-01T00:00:00.000000",
    "DFICycleCount": "0",
    "cleanCycleWaitTimeMinutes": "3",
    "unitStatus": "RDY",
    "isOnboarded": true,
    "deviceType": "udp",
    "litterRobotNickname": "Tesla Meowdel S",
    "cycleCount": "67",
    "panelLockActive": "0",
    "cyclesAfterDrawerFull": "0",
    "litterRobotSerial": "LR3C000000",
    "cycleCapacity": "46",
    "litterRobotId": "xxxxxxxxxxxxxx",
    "nightLightActive": "0",
    "didNotifyOffline": false,
    "isDFITriggered": "0",
    "sleepModeActive": "110:33:14"
  }
]
```

- `sleepModeActive`: either "0" or "1HH:mm:ss" where HH:mm:ss is number of hours, minutes and seconds since last sleep started. Sleep mode is between "100:00:00" and "108:00:00" (8 hours).

- `unitStatus`: is one of:

| Unit Status | Definition                   |
| ----------- | ---------------------------- |
| BR          | Bonnet Removed               |
| CSF         | Cat Sensor Fault             |
| SCF         | Cat Sensor Startup Fault     |
| CSI         | Cat Sensor Interrupted       |
| DHF         | Dump + Home Position Fault   |
| DPF         | Dump Position Fault          |
| HPF         | Home Position Fault          |
| OTF         | Over Torque Fault            |
| PD          | Pinch Detect                 |
| SPF         | Pinch Detect Startup Fault   |
| CST         | Cat Sensor Timing            |
| CCC         | Clean Cycle Complete         |
| CCP         | Clean Cycle In Progress      |
| DF1         | Drawer Is Full warning       |
| DF2         | Drawer Is Full no auto-cycle |
| DFS         | Drawer Is Full no auto-cycle |
| P           | Clean Cycle Paused           |
| RDY         | Ready                        |
| EC          | Empty Cycle                  |
| OFFLINE     | Offline                      |
| OFF         | Off                          |
| UNKNOWN     | Unknown                      |

### Commands

`POST https://v2.api.whisker.iothings.site/users/:user_id/robots/:robot_id/dispatch-commands`

**Security**: `Authorization`, `x-api-key`

**Request body (application/json)**:

```json
{
  "litterRobotId": "<litter robot id>",
  "command": "<command>"
}
```

| Command     | Action                                                                                                                                  |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| <C          | Start cleaning cycle                                                                                                                    |
| <W7         | Set wait time to 7 minutes                                                                                                              |
| <W3         | Set wait time to 3 minutes                                                                                                              |
| <WF         | Set wait time to 15 minutes                                                                                                             |
| <P0         | Turn off                                                                                                                                |
| <P1         | Turn on                                                                                                                                 |
| <N1         | Turn on night light                                                                                                                     |
| <N0         | Turn off night light                                                                                                                    |
| <S0         | Turn off sleep mode                                                                                                                     |
| <S119:45:02 | Turn on 8 hour sleep mode, offset by number of hours, minutes, and seconds since last sleep should start. E.g. 19 hours, 45 min, 2 sec. |
| <L1         | Turn on panel lock                                                                                                                      |
| <L0         | Turn off panel lock                                                                                                                     |

Response is one full robot entity.

### Settings & Resetting Tray

`PATCH https://v2.api.whisker.iothings.site/users/:user_id/robots/:robot_id`

body:

```json
{
  "litterRobotSerial": "LR3C000000",
  "cyclesAfterDrawerFull": "0",
  "litterRobotNickname": "Tesla Meowdel S",
  "cycleCount": "0",
  "cycleCapacity": "46"
}
```

Response is one full robot entity.

### Translations

Create a new `translations/sensor.<language code>.json` file that has the same keys found in `sensor.en.json`. See [frontend translations](https://github.com/home-assistant/frontend/tree/master/translations/frontend) for a list of other language codes (following the [BCP 47](https://tools.ietf.org/html/bcp47) standard).
