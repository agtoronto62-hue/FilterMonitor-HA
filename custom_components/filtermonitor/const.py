"""Constants for the FilterMonitor integration."""

DOMAIN = "filtermonitor"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_MAC_SUFFIX = "mac_suffix"
CONF_DEVICE_NAME = "device_name"

DEFAULT_PORT = 80
POLL_INTERVAL_SECONDS = 30

API_INFO = "/api/v1/info"
API_STATUS = "/api/v1/status"
API_SETPOINT = "/number/dp_high_pa/set"
API_UNIT_INWC_ON = "/switch/unit_inwc/turn_on"
API_UNIT_INWC_OFF = "/switch/unit_inwc/turn_off"
API_NTFY_ENABLE_ON = "/switch/ntfy_enable/turn_on"
API_NTFY_ENABLE_OFF = "/switch/ntfy_enable/turn_off"

MANUFACTURER = "AirScape"
MODEL = "FilterMonitor"

SETPOINT_MIN_PA = 25
SETPOINT_MAX_PA = 500
SETPOINT_STEP_PA = 5
