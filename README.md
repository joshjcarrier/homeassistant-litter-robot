# Litter-Robot 

The `litter-robot` component offers integration with the [Litter-Robot](https://www.litter-robot.com/litter-robot-iii-open-air-with-connect.html) WiFi enabled devices to [Home Assistant](https://www.home-assistant.io/).

![image](https://user-images.githubusercontent.com/526858/55675992-40ef6600-5880-11e9-8029-4abeeae37270.png)


## Install

Load this component by copying the entire directory as described in https://developers.home-assistant.io/docs/en/creating_component_loading.html . This is easiest with the Samba share add-on.


## Config

You'll need to have connected to your robot at least once before with the mobile app. Check out [this thread](https://community.smartthings.com/t/litter-robot-connect/106882/18) for more details.

Edit `/config/configuration.yaml`:

```yaml
litter_robot:
  username: "<your litter-robot open connect email>"
  password: "<your password>"
  api_key: "<your mobile app's API key>"
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
```

Then reload Groups config. This is easiest done with the frontend Configuration -> General -> Configuration reloading -> Reload groups.


## Development

Watch `/config/home-assistant.log`, which is accessible from the frontend via Developer tools -> (i) (/dev-info).


## TODO

* Multiple robots
  * Sensors uniquely identify robot
* More sensors
  * Sleep mode
* Services
  * Trigger cycle
