"""Config flow for OpenAI Voice integration."""

from __future__ import annotations

import asyncio
from typing import Any

import requests
import voluptuous as vol

from homeassistant import exceptions
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BASE_URL,
    CONF_STT_MODEL,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    DEFAULT_BASE_URL,
    DEFAULT_STT_MODEL,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_VOICE,
    DOMAIN,
    STT_MODELS,
    TTS_MODELS,
    TTS_VOICES,
    _LOGGER,
)


async def _validate_api_key(base_url: str, api_key: str) -> None:
    """Validate the API key by listing models."""
    url = f"{base_url}/models"
    response = await asyncio.to_thread(
        requests.get,
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    if response.status_code == 401:
        raise InvalidAPIKey
    if response.status_code == 403:
        raise UnauthorizedError
    if response.status_code not in (200, 404):
        raise CannotConnect


class OptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=self.config_entry.title,
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_STT_MODEL): vol.In(STT_MODELS),
                        vol.Required(CONF_TTS_MODEL): vol.In(TTS_MODELS),
                        vol.Required(CONF_TTS_VOICE): vol.In(TTS_VOICES),
                    }
                ),
                suggested_values={
                    CONF_STT_MODEL: self.config_entry.options.get(
                        CONF_STT_MODEL, DEFAULT_STT_MODEL
                    ),
                    CONF_TTS_MODEL: self.config_entry.options.get(
                        CONF_TTS_MODEL, DEFAULT_TTS_MODEL
                    ),
                    CONF_TTS_VOICE: self.config_entry.options.get(
                        CONF_TTS_VOICE, DEFAULT_TTS_VOICE
                    ),
                },
            ),
        )


class OpenAIVoiceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for OpenAI Voice."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL).rstrip("/")
            api_key = user_input[CONF_API_KEY]

            try:
                await _validate_api_key(base_url, api_key)
            except InvalidAPIKey:
                errors[CONF_API_KEY] = "invalid_api_key"
            except UnauthorizedError:
                errors["base"] = "unauthorized"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during validation")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="OpenAI Voice",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_BASE_URL: base_url,
                    },
                    options={
                        CONF_STT_MODEL: user_input.get(
                            CONF_STT_MODEL, DEFAULT_STT_MODEL
                        ),
                        CONF_TTS_MODEL: user_input.get(
                            CONF_TTS_MODEL, DEFAULT_TTS_MODEL
                        ),
                        CONF_TTS_VOICE: user_input.get(
                            CONF_TTS_VOICE, DEFAULT_TTS_VOICE
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): cv.string,
                    vol.Optional(
                        CONF_BASE_URL, default=DEFAULT_BASE_URL
                    ): cv.string,
                    vol.Required(
                        CONF_STT_MODEL, default=DEFAULT_STT_MODEL
                    ): vol.In(STT_MODELS),
                    vol.Required(
                        CONF_TTS_MODEL, default=DEFAULT_TTS_MODEL
                    ): vol.In(TTS_MODELS),
                    vol.Required(
                        CONF_TTS_VOICE, default=DEFAULT_TTS_VOICE
                    ): vol.In(TTS_VOICES),
                }
            ),
            errors=errors,
        )


class InvalidAPIKey(exceptions.HomeAssistantError):
    """Invalid API key."""


class UnauthorizedError(exceptions.HomeAssistantError):
    """Unauthorized."""


class CannotConnect(exceptions.HomeAssistantError):
    """Cannot connect."""
