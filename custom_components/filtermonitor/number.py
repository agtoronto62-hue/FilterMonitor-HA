"""Number platform for FilterMonitor."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_SETPOINT,
    CONF_DEVICE_NAME,
    CONF_MAC_SUFFIX,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SETPOINT_MAX_PA,
    SETPOINT_MIN_PA,
    SETPOINT_STEP_PA,
)
from .coordinator import FilterMonitorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FilterMonitor number entities."""
    coordinator: FilterMonitorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FilterMonitorSetpointNumber(coordinator, entry)])


class FilterMonitorSetpointNumber(
    CoordinatorEntity[FilterMonitorCoordinator], NumberEntity
):
    """High static setpoint number."""

    _attr_has_entity_name = True
    _attr_name = "High static setpoint"
    _attr_native_unit_of_measurement = UnitOfPressure.PA
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = SETPOINT_MIN_PA
    _attr_native_max_value = SETPOINT_MAX_PA
    _attr_native_step = SETPOINT_STEP_PA

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
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_setpoint_pa"

    @property
    def native_value(self) -> float | None:
        """Return setpoint in Pa."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("setpoint_pa")

    async def async_set_native_value(self, value: float) -> None:
        """Update setpoint on device."""
        rounded = int(round(value / SETPOINT_STEP_PA) * SETPOINT_STEP_PA)
        rounded = max(SETPOINT_MIN_PA, min(SETPOINT_MAX_PA, rounded))

        host = self._entry.data["host"]
        port = self._entry.data.get("port", DEFAULT_PORT)
        url = f"http://{host}:{port}{API_SETPOINT}?value={rounded}"

        session = async_get_clientsession(self.hass)
        async with session.post(url, timeout=10) as response:
            response.raise_for_status()

        await self.coordinator.async_request_refresh()
