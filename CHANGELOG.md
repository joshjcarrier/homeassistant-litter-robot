# HomeAssistant Litter Robot Changelog

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
