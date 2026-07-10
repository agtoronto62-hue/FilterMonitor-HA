"""DataUpdateCoordinator for FilterMonitor."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_INFO, API_STATUS, DEFAULT_PORT, DOMAIN, POLL_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class FilterMonitorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch status from a FilterMonitor device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        host = entry.data["host"]
        port = entry.data.get("port", DEFAULT_PORT)
        self.api_base = f"http://{host}:{port}"

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data.get('mac_suffix', host)}",
            update_interval=timedelta(seconds=POLL_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll device status."""
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(
                f"{self.api_base}{API_STATUS}",
                timeout=10,
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with FilterMonitor: {err}") from err

    async def async_fetch_info(self) -> dict[str, Any]:
        """Fetch static device info (used during config flow)."""
        session = async_get_clientsession(self.hass)
        async with session.get(
            f"{self.api_base}{API_INFO}",
            timeout=10,
        ) as response:
            response.raise_for_status()
            return await response.json()
