# Litter-Robot 

The `litter-robot` component offers integration with the [Litter-Robot](https://www.litter-robot.com/litter-robot-iii-open-air-with-connect.html) WiFi enabled devices to [Home Assistant](https://www.home-assistant.io/).

> 🍻 I'm not employed by Litter Robot, and provide this plugin purely for our own enjoyment. 
>
> Use [my referal code](http://share.litter-robot.com/rmc2b) and get $25 off your own robot (and it tips me too!) 

![image](https://user-images.githubusercontent.com/526858/55689115-c8e37780-5935-11e9-979d-298452e87054.png)


## Install

Load this component by copying the entire directory as described in https://developers.home-assistant.io/docs/en/creating_component_loading.html . This is easiest with the Samba share add-on.


## Config

You'll need to have connected to your robot at least once before with the mobile app. 

🔑 Trouble finding the API key? Search for `x-api-key` in [this thread](https://community.smartthings.com/t/litter-robot-connect/106882/18) for more details.

Edit `/config/configuration.yaml`. For a robot nicknamed "Tesla Meowdel S":

```yaml
litter_robot:
  username: "<your litter-robot open connect email>"
  password: "<your password>"
  api_key: "<litter robot app API key>"

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
        value_template: "{{ is_state('sensor.litter_robot_tesla_meowdel_s_status', 'Clean Cycling') }}"
        icon_template: "mdi:refresh"
        turn_on:
          service: litter_robot.cycle
        turn_off:
```

Restart HASS to activate the component and to reapply config changes. This can be done from the frontend via Configuration -> General -> Server management -> Restart.


## Grouping Sensors

Discover the list by searching "litter_robot" in the frontend: Developer tools -> <> (States).

Edit `/config/groups.yaml`. For a robot nicknamed "Tesla Meowdel S":

```yaml
Tesla Meowdel S:
  control: hidden
  entities:
    - sensor.litter_robot_tesla_meowdel_s_status
    - sensor.litter_robot_tesla_meowdel_s_waste
    - switch.litter_robot_cycle
    - switch.litter_robot_nightlight
```

Then reload Groups config. This is easiest done with the frontend Configuration -> General -> Configuration reloading -> Reload groups.


## Development

Watch `/config/home-assistant.log`, which is accessible from the frontend via Developer tools -> (i) (/dev-info).

### State

`GET /users/:user_id/litter-robots`

```json
[{
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
}]
```

* `sleepModeActive`: either "0" or "1HH:mm:ss" where HH:mm:ss is number of hours, minutes and seconds since last sleep started. Sleep mode is between "100:00:00" and "108:00:00" (8 hours).

* `unitStatus`: is one of:
```
"RDY" == Unit ready to be used.
"CCP" == Cleaning Cycle in Progress
"CCC" == Cleaning Cycle Completed
"DF1" == Drawer is Full -- But it is able to cycle a few more times.
"DF2" == Drawer is Full -- But it is still able to cycle a few more times.
"CST" == Cat sensor timing
"CSI" == Cat sensor interrupt
"BR" == Bonnet removed
"P" == Unit is Paused
"OFF" == Unit is turned off
"SDF" == Drawer is completely full and will not cycle.
"DFS" == Drawer is completely full and will not cycle. 
```

### Commands

```
"<C" == Start cleaning cycle
"<W7" == Set wait time to 7 minutes
"<W3" == Set wait time to 3 minutes
"<WF" == Set wait time to 15 minutes
"<P0" == Turn off
"<P1" == Turn on
"<N1" == Turn on night light
"<N0" == Turn off night light
"<S0" == Turn off sleep mode
"<S119:45:02" == Turn on sleep mode, followed by number of hours, minutes, and seconds since last sleep started. E.g. 19 hours, 45 min, 2 sec.
"<L1" == Turn on panel lock
"<L0" == Turn off panel lock
```

### Settings & Resetting Tray

`PATCH /users/:user_id/litter-robots/:robot_id`

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

## TODO

* [More sensors](https://community.smartthings.com/t/litter-robot-connect/106882/19)
  * Mark drawer empty
* Multiple robots
  * Sensors uniquely identify robot

