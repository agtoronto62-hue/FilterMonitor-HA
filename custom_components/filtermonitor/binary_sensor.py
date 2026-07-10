"""Binary sensor platform for FilterMonitor."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME, CONF_MAC_SUFFIX, DOMAIN, MANUFACTURER, MODEL
from .coordinator import FilterMonitorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FilterMonitor binary sensors."""
    coordinator: FilterMonitorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FilterMonitorHighStaticSensor(coordinator, entry)])


class FilterMonitorHighStaticSensor(
    CoordinatorEntity[FilterMonitorCoordinator], BinarySensorEntity
):
    """High static alarm binary sensor."""

    _attr_has_entity_name = True
    _attr_name = "High static"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

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

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_high_static"

    @property
    def is_on(self) -> bool | None:
        """Return alarm state."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("high_static")
