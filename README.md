# Litter-Robot 

The `litter-robot` component offers integration with the [Litter-Robot](https://www.litter-robot.com/litter-robot-iii-open-air-with-connect.html) WiFi enabled devices to [Home Assistant](https://www.home-assistant.io/).

![image](https://user-images.githubusercontent.com/526858/43360926-d22c234a-9276-11e8-8471-9bc8b3b7d811.png)


## Install

Load this component by copying the entire directory as described in https://developers.home-assistant.io/docs/en/creating_component_loading.html


## Config

Edit `/config/configuration.yaml`:

```yaml
litter_robot:
  username: "<your litter-robot open connect email>"
  password: "<your password>"
  api_key: "<your mobile app's API key>"
```

Restart HASS to activate the component and to reapply config changes.


## Grouping Sensors

Edit `/config/groups.yaml`:

```yaml
Tesla Meowdel S:
  - sensor.litterrobot_status
  - sensor.litterrobot_waste
```

Then reload Groups.


## Development

Watch `/config/home-assistant.log`.


## TODO

* Multiple robots
  * Sensors uniquely identify robot
* More sensors
  * Sleep mode
* Services
  * Trigger cycle
