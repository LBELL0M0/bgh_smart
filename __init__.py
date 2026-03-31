"""The BGH Smart Control integration."""
from __future__ import annotations

import logging
from typing import Any

try:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant
    from homeassistant.exceptions import ConfigEntryNotReady
    HAS_HOMEASSISTANT = True
except ModuleNotFoundError:
    # Allow importing package modules (for local CLI tools) without HA installed.
    ConfigEntry = Any  # type: ignore[assignment]
    HomeAssistant = Any  # type: ignore[assignment]
    Platform = str  # type: ignore[assignment]

    class ConfigEntryNotReady(RuntimeError):
        """Fallback error when Home Assistant is unavailable."""

    HAS_HOMEASSISTANT = False

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE] if HAS_HOMEASSISTANT else ["climate"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BGH Smart Control from a config entry."""
    if not HAS_HOMEASSISTANT:
        raise RuntimeError("Home Assistant is required to set up this integration")

    from .coordinator import BGHDataUpdateCoordinator

    hass.data.setdefault(DOMAIN, {})

    coordinator = BGHDataUpdateCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Error setting up BGH Smart Control: %s", err)
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
