"""ElevenLabs boundary for metadata verification and explicit narration generation.

The adapter deliberately uses the standard library. Provider calls that create
audio are allowed only from an approval-gated production command; this module
does not decide whether a generation is authorized.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ElevenLabsError(RuntimeError):
    """A safe-to-display ElevenLabs adapter failure."""


@dataclass(frozen=True)
class ElevenLabsVoice:
    """The small, provider-neutral subset needed to select a narrator."""

    voice_id: str
    name: str


def load_local_env_value(env_path: Path, variable_name: str) -> str | None:
    """Read one simple ``KEY=value`` setting from an untracked local .env file.

    Existing process environment takes precedence.  The loader intentionally
    accepts only the simple format used by this repository's .env.example.
    """
    value = os.getenv(variable_name)
    if value:
        return value

    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None

    prefix = f"{variable_name}="
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith(prefix):
            configured_value = line[len(prefix) :].strip()
            return configured_value or None
    return None


class ElevenLabsClient:
    """Small HTTP client for provider metadata and explicit speech synthesis."""

    _API_ROOT = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str, *, timeout_seconds: float = 20.0) -> None:
        if not api_key.strip():
            raise ElevenLabsError("ELEVENLABS_API_KEY is missing or empty")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_local_environment(cls, repository_root: Path) -> "ElevenLabsClient":
        api_key = load_local_env_value(repository_root / ".env", "ELEVENLABS_API_KEY")
        if api_key is None:
            raise ElevenLabsError("ELEVENLABS_API_KEY is missing or empty")
        return cls(api_key)

    def list_voices(self) -> tuple[ElevenLabsVoice, ...]:
        """Return accessible voices without generating audio or spending credits."""
        payload = self._get_json("/voices")
        entries = payload.get("voices")
        if not isinstance(entries, list):
            raise ElevenLabsError("ElevenLabs returned an invalid voices response")

        voices: list[ElevenLabsVoice] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            voice_id = entry.get("voice_id")
            name = entry.get("name")
            if isinstance(voice_id, str) and isinstance(name, str):
                voices.append(ElevenLabsVoice(voice_id=voice_id, name=name))
        return tuple(voices)

    def synthesize_narration(self, voice_id: str, text: str, output_path: Path) -> Path:
        """Create one approved narration MP3 and save it outside version control."""
        if not voice_id or not text.strip():
            raise ElevenLabsError("voice ID and narration text are required")
        body = json.dumps(
            {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.58,
                    "similarity_boost": 0.75,
                    "style": 0.12,
                    "use_speaker_boost": True,
                    "speed": 0.94,
                },
            }
        ).encode("utf-8")
        request = Request(
            f"{self._API_ROOT}/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            data=body,
            headers={
                "xi-api-key": self._api_key,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                audio = response.read()
        except HTTPError as error:
            if error.code in (401, 403):
                raise ElevenLabsError("ElevenLabs rejected the API key or voice access") from error
            raise ElevenLabsError(f"ElevenLabs narration request failed with HTTP {error.code}") from error
        except (URLError, TimeoutError) as error:
            raise ElevenLabsError("could not reach ElevenLabs") from error
        if not audio:
            raise ElevenLabsError("ElevenLabs returned empty narration audio")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        return output_path

    def _get_json(self, path: str) -> dict[str, Any]:
        request = Request(
            f"{self._API_ROOT}{path}",
            headers={"xi-api-key": self._api_key, "Accept": "application/json"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                decoded: Any = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in (401, 403):
                raise ElevenLabsError(
                    "ElevenLabs rejected the API key or its required Voices read permission"
                ) from error
            raise ElevenLabsError(f"ElevenLabs request failed with HTTP {error.code}") from error
        except (URLError, TimeoutError) as error:
            raise ElevenLabsError("could not reach ElevenLabs") from error
        except json.JSONDecodeError as error:
            raise ElevenLabsError("ElevenLabs returned invalid JSON") from error

        if not isinstance(decoded, dict):
            raise ElevenLabsError("ElevenLabs returned an invalid response")
        return decoded
