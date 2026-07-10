"""Config flow for FilterMonitor."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

try:
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:
    from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_DEVICE_NAME,
    CONF_MAC_SUFFIX,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)

_LOGGER = logging.getLogger(__name__)


def _decode_prop(properties: dict[str, str | bytes | None], key: str) -> str:
    value = properties.get(key)
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


class FilterMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FilterMonitor."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._discovery_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle manual setup by IP/hostname."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            api_base = f"http://{host}:{port}"

            try:
                session = async_get_clientsession(self.hass)
                async with session.get(
                    f"{api_base}/api/v1/info",
                    timeout=10,
                ) as response:
                    response.raise_for_status()
                    info = await response.json()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                mac_suffix = info.get("mac_suffix", host)
                await self.async_set_unique_id(f"filtermonitor_{mac_suffix}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info.get("device_name", f"FilterMonitor {mac_suffix}"),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_MAC_SUFFIX: mac_suffix,
                        CONF_DEVICE_NAME: info.get("device_name", ""),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> config_entries.ConfigFlowResult:
        """Handle Zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        properties = discovery_info.properties

        mac_suffix = _decode_prop(properties, "mac")
        api_version = _decode_prop(properties, "api")
        firmware = _decode_prop(properties, "version")

        unique_id = f"filtermonitor_{mac_suffix}" if mac_suffix else None
        if unique_id:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

        api_base = f"http://{host}:{port}"
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                f"{api_base}/api/v1/info",
                timeout=10,
            ) as response:
                response.raise_for_status()
                info = await response.json()
        except Exception:
            return self.async_abort(reason="cannot_connect")

        if info.get("api_version") != 1:
            return self.async_abort(reason="unsupported_api")

        device_name = info.get("device_name") or discovery_info.name or MODEL
        mac_suffix = info.get("mac_suffix", mac_suffix)

        self._discovery_info = {
            CONF_HOST: host,
            CONF_PORT: port,
            CONF_MAC_SUFFIX: mac_suffix,
            CONF_DEVICE_NAME: device_name,
            "firmware": firmware or info.get("firmware", ""),
            "api_version": api_version or str(info.get("api_version", "")),
        }

        self.context["title_placeholders"] = {
            "name": device_name,
            "model": MODEL,
            "manufacturer": MANUFACTURER,
        }

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm discovered or prepared device."""
        if user_input is not None:
            info = self._discovery_info
            mac_suffix = info[CONF_MAC_SUFFIX]
            await self.async_set_unique_id(f"filtermonitor_{mac_suffix}")

            return self.async_create_entry(
                title=info.get(CONF_DEVICE_NAME, f"FilterMonitor {mac_suffix}"),
                data={
                    CONF_HOST: info[CONF_HOST],
                    CONF_PORT: info[CONF_PORT],
                    CONF_MAC_SUFFIX: mac_suffix,
                    CONF_DEVICE_NAME: info.get(CONF_DEVICE_NAME, ""),
                },
            )

        info = self._discovery_info
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": info[CONF_HOST],
                "device_name": info.get(CONF_DEVICE_NAME, ""),
                "firmware": info.get("firmware", ""),
                "mac_suffix": info.get(CONF_MAC_SUFFIX, ""),
            },
        )
