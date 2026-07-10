"""Sensor platform for FilterMonitor."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
    UnitOfTemperature,
)
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
    """Set up FilterMonitor sensors."""
    coordinator: FilterMonitorCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        FilterMonitorPressureSensor(coordinator, entry),
        FilterMonitorTemperatureSensor(coordinator, entry),
        FilterMonitorFirmwareSensor(coordinator, entry),
        FilterMonitorIpSensor(coordinator, entry),
        FilterMonitorSsidSensor(coordinator, entry),
        FilterMonitorWifiRssiSensor(coordinator, entry),
    ]
    async_add_entities(entities)


class FilterMonitorEntity(CoordinatorEntity[FilterMonitorCoordinator], SensorEntity):
    """Base FilterMonitor sensor."""

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


class FilterMonitorPressureSensor(FilterMonitorEntity):
    """Differential pressure sensor."""

    _attr_name = "Differential pressure"
    _attr_native_unit_of_measurement = UnitOfPressure.PA
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_dp_pa"

    @property
    def native_value(self) -> int | None:
        """Return pressure in Pa."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("dp_pa")


class FilterMonitorTemperatureSensor(FilterMonitorEntity):
    """Air temperature sensor."""

    _attr_name = "Air temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_temp_c"

    @property
    def available(self) -> bool:
        """Return availability."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("temp_valid", False)
        )

    @property
    def native_value(self) -> float | None:
        """Return temperature in °C."""
        if not self.coordinator.data or not self.coordinator.data.get("temp_valid"):
            return None
        return self.coordinator.data.get("temp_c")


class FilterMonitorFirmwareSensor(FilterMonitorEntity):
    """Firmware version diagnostic sensor."""

    _attr_name = "Firmware version"
    _attr_entity_category = "diagnostic"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_firmware"

    @property
    def native_value(self) -> str | None:
        """Return firmware version."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("firmware")


class FilterMonitorIpSensor(FilterMonitorEntity):
    """IP address diagnostic sensor."""

    _attr_name = "IP address"
    _attr_entity_category = "diagnostic"
    _attr_icon = "mdi:ip-network"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_ip"

    @property
    def native_value(self) -> str | None:
        """Return IP address."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("ip_address")


class FilterMonitorSsidSensor(FilterMonitorEntity):
    """Connected SSID diagnostic sensor."""

    _attr_name = "Connected SSID"
    _attr_entity_category = "diagnostic"
    _attr_icon = "mdi:wifi"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_ssid"

    @property
    def native_value(self) -> str | None:
        """Return SSID."""
        if not self.coordinator.data:
            return None
        ssid = self.coordinator.data.get("connected_ssid")
        if ssid in (None, "--"):
            return None
        return ssid


class FilterMonitorWifiRssiSensor(FilterMonitorEntity):
    """Wi-Fi signal strength diagnostic sensor."""

    _attr_name = "Wi-Fi signal"
    _attr_entity_category = "diagnostic"
    _attr_icon = "mdi:wifi-strength-2"
    _attr_native_unit_of_measurement = "dBm"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"filtermonitor_{self._entry.data[CONF_MAC_SUFFIX]}_wifi_rssi"

    @property
    def native_value(self) -> int | None:
        """Return RSSI in dBm (displayed as numeric)."""
        if not self.coordinator.data:
            return None
        rssi = self.coordinator.data.get("wifi_rssi")
        if rssi is None or rssi <= -127:
            return None
        return rssi
