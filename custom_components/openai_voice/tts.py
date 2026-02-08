"""OpenAI text-to-speech entity."""

from __future__ import annotations

import asyncio
from typing import Any

import requests
from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.components.tts.models import Voice
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BASE_URL,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_VOICE,
    SUPPORTED_LANGUAGES,
    TTS_VOICES,
    _LOGGER,
)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI TTS from a config entry."""
    async_add_entities(
        [
            OpenAITTSEntity(
                config_entry.data[CONF_API_KEY],
                config_entry.data[CONF_BASE_URL],
                config_entry.options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL),
                config_entry.options.get(CONF_TTS_VOICE, DEFAULT_TTS_VOICE),
                config_entry.entry_id,
            )
        ]
    )


class OpenAITTSEntity(TextToSpeechEntity):
    """OpenAI TTS entity."""

    _attr_supported_options = ["voice"]

    def __init__(
            self,
            api_key: str,
            base_url: str,
            model: str,
            voice: str,
            unique_id: str,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._voice = voice
        self._attr_name = "OpenAI TTS"
        self._attr_unique_id = unique_id + "_tts"
        self._attr_default_language = "en"
        self._attr_supported_languages = SUPPORTED_LANGUAGES

    @callback
    def async_get_supported_voices(self, language: str) -> list[Voice] | None:
        return [Voice(voice_id=v, name=v) for v in TTS_VOICES]

    async def async_get_tts_audio(
            self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Generate speech from text."""
        voice = options.get("voice", self._voice)

        try:
            response = await asyncio.to_thread(
                self._call_api, message, voice
            )

            if response.status_code != 200:
                _LOGGER.error(
                    "OpenAI TTS request failed: %d %s",
                    response.status_code,
                    response.text,
                )
                return (None, None)

            return ("mp3", response.content)

        except Exception:
            _LOGGER.exception("OpenAI TTS request failed")
            return (None, None)

    def _call_api(self, message: str, voice: str) -> requests.Response:
        """Make the blocking API call."""
        return requests.post(
            f"{self._base_url}/audio/speech",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "input": message,
                "voice": voice,
                "response_format": "mp3",
            },
            timeout=30,
        )
