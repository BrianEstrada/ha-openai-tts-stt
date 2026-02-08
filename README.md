# OpenAI Voice for Home Assistant

A custom Home Assistant integration that adds OpenAI-powered speech-to-text (Whisper) and text-to-speech to the Assist voice pipeline.

## Features

- **STT**: Transcribe speech using OpenAI's Whisper API (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`)
- **TTS**: Generate speech using OpenAI's TTS API (`tts-1`, `tts-1-hd`) with 9 voice options
- **Custom endpoints**: Point at any OpenAI-compatible API (Groq, Mistral, local models, etc.) via the base URL setting
- **Zero dependencies**: Uses only libraries already bundled with Home Assistant

## Installation

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, go to **Integrations** > three-dot menu > **Custom repositories**
3. Add `https://github.com/BrianEstrada/ha-openai-tts-stt` with category **Integration**
4. Install **OpenAI Voice** and restart Home Assistant

## Setup

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **OpenAI Voice**
3. Enter your OpenAI API key and select your preferred models/voice
4. Go to **Settings > Voice Assistants** and select **OpenAI STT** / **OpenAI TTS** in your assistant config

## Configuration

| Option | Description | Default |
|--------|-------------|---------|
| API Key | Your OpenAI API key | — |
| API Base URL | OpenAI-compatible API endpoint | `https://api.openai.com/v1` |
| STT Model | Speech-to-text model | `whisper-1` |
| TTS Model | Text-to-speech model | `tts-1` |
| TTS Voice | Default voice | `alloy` |

Models and voice can be changed after setup via the integration's **Configure** button.

## Available Voices

`alloy`, `ash`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, `shimmer`
