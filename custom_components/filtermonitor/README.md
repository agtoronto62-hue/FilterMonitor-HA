# FilterMonitor — Home Assistant Integration

Adds FilterMonitor air-filter pressure monitors to Home Assistant via **Zeroconf discovery** and **local HTTP** (no MQTT broker configuration required).

## Requirements

- Home Assistant **2024.1** or later
- FilterMonitor firmware with API v1 (**FMV10.3+** recommended; current release **FMV10.8**)
- Device and Home Assistant on the same LAN

## Installation

### Manual copy

1. Copy the `custom_components/filtermonitor` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services** — FilterMonitor should appear under **Discovered**.
4. Click **Configure** → **Submit**.

### HACS (custom repository)

1. In HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/AirScapeFans/FilterMonitor-HA` as category **Integration**
3. Install **FilterMonitor** from HACS
4. Restart Home Assistant

## Manual setup (if discovery fails)

**Settings → Devices & Services → Add Integration → FilterMonitor**

Enter hostname or IP, e.g. `filtermonitor-1cb440.local`, an optional mDNS alias such as `prdfm.local`, or `192.168.68.58`.

## Entities

| Entity | Description |
|--------|-------------|
| Differential pressure | Corrected ΔP (Pa) |
| Air temperature | °C |
| High static | Binary alarm |
| High static setpoint | Adjustable 25–500 Pa |
| Display in inWC | UI unit preference (Pa vs inWC) |
| ntfy alerts enabled | Push notification toggle |
| Firmware version | Diagnostic |
| IP address | Diagnostic |
| Connected SSID | Diagnostic |
| Wi-Fi signal | RSSI (dBm) |

## Polling

Status is polled every **30 seconds** from `GET /api/v1/status`.

Setpoint changes use `POST /number/dp_high_pa/set`.

Switches use the same ESPHome-style routes as MQTT discovery (`/switch/unit_inwc/*`, `/switch/ntfy_enable/*`).

## Troubleshooting

- **Not discovered:** Confirm `_filtermonitor._tcp` is visible (`dns-sd -B _filtermonitor._tcp` on Windows, `avahi-browse` on Linux).
- **Cannot connect:** Use the device IP instead of `.local` if mDNS is blocked on your router.
- **Duplicate MQTT entities:** On the device web UI, set the active path to **HACS** (this disables MQTT). Do not use both paths at once.
- **HACS not discovered:** Device must be in **HACS** mode on the Home Assistant web page so `_filtermonitor._tcp` is advertised.

## Development

See `docs/FilterMonitor-Home-Assistant-Integration-Plan.md` in the firmware repository: https://github.com/AirScapeFans/FilterMonitor
