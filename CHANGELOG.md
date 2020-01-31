# HomeAssistant Litter Robot Changelog

## 2020-01-30

- Unrecognized state codes reported as code instead of crashing the sensor
- New state code "CSF"
- Refresh interval reduced from 5 min to 2 min to catch state changes (avg cycle ~2m:30s)

## 2019-12-07

- Backend API and authentication change to match latest iOS app

The `api_key` configuration key is no longer used and should be deleted before the component is reloaded.

```diff
litter_robot:
  username: "<your litter-robot open connect email>"
  password: "<your password>"
- api_key: "<previous api key>"
```

## 2019-08-06

- Multiple Litter Robots under one account will now be registered
