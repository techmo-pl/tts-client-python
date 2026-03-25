"""Integration tests — require a live TTS service.

These tests are excluded from the default pytest run (see pytest.ini addopts).
Run them explicitly:

    TTS_SERVICE_ADDRESS=host:port pytest -m integration

Optional environment variables:
    TTS_VOICE_NAME      — voice name passed to --voice-name (default: service default)
    TTS_LANGUAGE_CODE   — ISO 639-1 language code (default: service default)
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_synthesize_generates_audio_file(tts_service_address, tmp_path):
    """Verify the TTS service produces a non-empty WAV audio file."""
    from tts_client_python.general import synthesize

    output = tmp_path / "output.wav"

    synthesize(
        service_address=tts_service_address,
        tls=False,
        tls_dir="",
        tls_ca_cert_file="",
        tls_cert_file="",
        tls_private_key_file="",
        session_id="",
        grpc_timeout=10_000,
        audio_encoding="pcm16",
        sampling_rate=0,
        max_frame_size=0,
        language_code=os.environ.get("TTS_LANGUAGE_CODE", ""),
        voice_name=os.environ.get("TTS_VOICE_NAME", ""),
        voice_age="",
        voice_gender="",
        voice_variant=1,
        speech_pitch=1.0,
        speech_range=1.0,
        speech_rate=1.0,
        speech_stress=1.0,
        speech_volume=1.0,
        play=False,
        response="streaming",
        out_path=str(output),
        text="Test audio synthesis.",
    )

    assert output.exists(), f"Audio file was not created — check TTS_SERVICE_ADDRESS={tts_service_address}"
    assert output.stat().st_size > 0, "Audio file was created but is empty"
