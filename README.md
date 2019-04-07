# Litter-Robot 

The `litter-robot` component offers integration with the [Litter-Robot](https://www.litter-robot.com/litter-robot-iii-open-air-with-connect.html) WiFi enabled devices to [Home Assistant](https://www.home-assistant.io/).

![image](https://user-images.githubusercontent.com/526858/55680400-fbf22080-58cd-11e9-81de-9ea2aeff5bd9.png)


## Install

Load this component by copying the entire directory as described in https://developers.home-assistant.io/docs/en/creating_component_loading.html . This is easiest with the Samba share add-on.


## Config

You'll need to have connected to your robot at least once before with the mobile app. Check out [this thread](https://community.smartthings.com/t/litter-robot-connect/106882/18) for more details.

Edit `/config/configuration.yaml`. For a robot nicknamed "Tesla Meowdel S":

```yaml
litter_robot:
  username: "<your litter-robot open connect email>"
  password: "<your password>"
  api_key: "<your mobile app's API key>"

switch:
  - platform: template
    switches:
      litter_robot_nightlight_on:
        friendly_name: "Tesla Meowdel S Night Light On"
        value_template: false
        icon_template: "mdi:lightbulb-on"
        turn_on:
          service: litter_robot.nightlight_turn_on
        turn_off:
      litter_robot_nightlight_off:
        friendly_name: "Tesla Meowdel S Night Light Off"
        value_template: false
        icon_template: "mdi:lightbulb"
        turn_on:
          service: litter_robot.nightlight_turn_off
        turn_off:
      litter_robot_cycle:
        friendly_name: "Tesla Meowdel S Cycle"
        value_template: false
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
    - switch.litter_robot_nightlight_on
    - switch.litter_robot_nightlight_off
```

Then reload Groups config. This is easiest done with the frontend Configuration -> General -> Configuration reloading -> Reload groups.


## Development

Watch `/config/home-assistant.log`, which is accessible from the frontend via Developer tools -> (i) (/dev-info).


## TODO

* [More sensors](https://community.smartthings.com/t/litter-robot-connect/106882/19)
  * Sleep mode as part of state
  * Night light status
* Multiple robots
  * Sensors uniquely identify robot

