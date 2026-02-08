"""OpenAI Whisper speech-to-text entity."""

from __future__ import annotations

import asyncio
import io
import wave
from collections.abc import AsyncIterable

import requests
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    SpeechToTextEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BASE_URL,
    CONF_STT_MODEL,
    DEFAULT_STT_MODEL,
    SUPPORTED_LANGUAGES,
    _LOGGER,
)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI STT from a config entry."""
    async_add_entities(
        [
            OpenAISTTEntity(
                config_entry.data[CONF_API_KEY],
                config_entry.data[CONF_BASE_URL],
                config_entry.options.get(CONF_STT_MODEL, DEFAULT_STT_MODEL),
                config_entry.entry_id,
            )
        ]
    )


class OpenAISTTEntity(SpeechToTextEntity):
    """OpenAI Whisper STT entity."""

    def __init__(
            self,
            api_key: str,
            base_url: str,
            model: str,
            unique_id: str,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._attr_name = "OpenAI STT"
        self._attr_unique_id = unique_id + "_stt"

    @property
    def supported_languages(self) -> list[str]:
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[AudioFormats]:
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
            self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        """Process audio stream and return transcription."""
        pcm_data = b""
        async for chunk in stream:
            pcm_data += chunk

        if not pcm_data:
            _LOGGER.error("No audio data received")
            return SpeechResult("", SpeechResultState.ERROR)

        # Wrap raw PCM in a WAV container
        wav_buf = io.BytesIO()
        with wave.open(wav_buf, "wb") as wf:
            wf.setnchannels(metadata.channel)
            wf.setsampwidth(2)
            wf.setframerate(metadata.sample_rate)
            wf.writeframes(pcm_data)
        wav_buf.seek(0)

        try:
            response = await asyncio.to_thread(
                self._call_api, wav_buf, metadata.language
            )

            if response.status_code != 200:
                _LOGGER.error(
                    "OpenAI STT request failed: %d %s",
                    response.status_code,
                    response.text,
                )
                return SpeechResult("", SpeechResultState.ERROR)

            text = response.json().get("text", "")
            _LOGGER.debug("Transcription: %s", text)

            if not text:
                return SpeechResult("", SpeechResultState.ERROR)

            return SpeechResult(text, SpeechResultState.SUCCESS)

        except Exception:
            _LOGGER.exception("OpenAI STT request failed")
            return SpeechResult("", SpeechResultState.ERROR)

    def _call_api(self, wav_buf: io.BytesIO, language: str | None) -> requests.Response:
        """Make the blocking API call."""
        data: dict = {
            "model": self._model,
            "response_format": "json",
        }
        if language:
            data["language"] = language

        return requests.post(
            f"{self._base_url}/audio/transcriptions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={"file": ("audio.wav", wav_buf, "audio/wav")},
            data=data,
            timeout=30,
        )
