"""Switch platform for FilterMonitor."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_NTFY_ENABLE_OFF,
    API_NTFY_ENABLE_ON,
    API_UNIT_INWC_OFF,
    API_UNIT_INWC_ON,
    CONF_DEVICE_NAME,
    CONF_MAC_SUFFIX,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)
from .coordinator import FilterMonitorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FilterMonitor switches."""
    coordinator: FilterMonitorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FilterMonitorUnitInwcSwitch(coordinator, entry),
            FilterMonitorNtfyEnableSwitch(coordinator, entry),
        ]
    )


class FilterMonitorSwitch(CoordinatorEntity[FilterMonitorCoordinator], SwitchEntity):
    """Base FilterMonitor switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FilterMonitorCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._entry = entry
        mac_suffix = entry.data[CONF_MAC_SUFFIX]
        device_name = entry.data.get(CONF_DEVICE_NAME) or f"FilterMonitor {mac_suffix}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_suffix)},
            name=device_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=coordinator.data.get("firmware") if coordinator.data else None,
        )

    async def _post_switch(self, path: str) -> None:
        """POST to device switch endpoint."""
        host = self._entry.data["host"]
        port = self._entry.data.get("port", DEFAULT_PORT)
        url = f"http://{host}:{port}{path}"

        session = async_get_clientsession(self.hass)
        async with session.post(url, timeout=10) as response:
            response.raise_for_status()

        await self.coordinator.async_request_refresh()


class FilterMonitorUnitInwcSwitch(FilterMonitorSwitch):
    """Display pressure in inches of water column."""

    _attr_name = "Display in inWC"
    _attr_icon = "mdi:ruler"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_unit_inwc"

    @property
    def is_on(self) -> bool | None:
        """Return display unit preference."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("unit_inwc")

    async def async_turn_on(self, **kwargs) -> None:
        """Enable inWC display units."""
        await self._post_switch(API_UNIT_INWC_ON)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable inWC display units."""
        await self._post_switch(API_UNIT_INWC_OFF)


class FilterMonitorNtfyEnableSwitch(FilterMonitorSwitch):
    """ntfy push notification enable."""

    _attr_name = "ntfy alerts enabled"
    _attr_icon = "mdi:bell-outline"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_ntfy_enable"

    @property
    def is_on(self) -> bool | None:
        """Return ntfy enable state."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("ntfy_enabled")

    async def async_turn_on(self, **kwargs) -> None:
        """Enable ntfy alerts."""
        await self._post_switch(API_NTFY_ENABLE_ON)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable ntfy alerts."""
        await self._post_switch(API_NTFY_ENABLE_OFF)
