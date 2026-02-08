"""Constants for OpenAI Voice integration."""

import logging

DOMAIN = "openai_voice"

_LOGGER = logging.getLogger(__name__)

CONF_BASE_URL = "base_url"
CONF_STT_MODEL = "stt_model"
CONF_TTS_MODEL = "tts_model"
CONF_TTS_VOICE = "tts_voice"
CONF_TEMPERATURE = "temperature"
CONF_PROMPT = "prompt"

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_STT_MODEL = "whisper-1"
DEFAULT_TTS_MODEL = "tts-1"
DEFAULT_TTS_VOICE = "alloy"
DEFAULT_TEMPERATURE = 0
DEFAULT_PROMPT = ""

TTS_VOICES = [
    "alloy",
    "ash",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
]

STT_MODELS = [
    "whisper-1",
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
]

TTS_MODELS = [
    "tts-1",
    "tts-1-hd",
]

SUPPORTED_LANGUAGES = [
    "af", "ar", "hy", "az", "be", "bs", "bg", "ca",
    "zh", "hr", "cs", "da", "nl", "en", "et", "fi",
    "fr", "gl", "de", "el", "he", "hi", "hu", "is",
    "id", "it", "ja", "kn", "kk", "ko", "lv", "lt",
    "mk", "ms", "mr", "mi", "ne", "no", "fa", "pl",
    "pt", "ro", "ru", "sr", "sk", "sl", "es", "sw",
    "sv", "tl", "ta", "th", "tr", "uk", "ur", "vi", "cy",
]
