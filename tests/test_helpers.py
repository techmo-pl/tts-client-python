"""Unit tests for helper functions in general.py (encoding, path, voice, config)."""

from __future__ import annotations

import pytest

from tts_client_python.general import create_out_path, create_voice, get_audio_encoding, prepare_synthesis_config
from tts_client_python.proto import techmo_tts_pb2


class TestGetAudioEncoding:
    def test_pcm16(self):
        assert get_audio_encoding("pcm16") == techmo_tts_pb2.AudioEncoding.PCM16  # type: ignore[attr-defined]

    def test_ogg_vorbis(self):
        assert get_audio_encoding("ogg-vorbis") == techmo_tts_pb2.AudioEncoding.OGG_VORBIS  # type: ignore[attr-defined]

    def test_ogg_opus(self):
        assert get_audio_encoding("ogg-opus") == techmo_tts_pb2.AudioEncoding.OGG_OPUS  # type: ignore[attr-defined]

    def test_a_law(self):
        assert get_audio_encoding("a-law") == techmo_tts_pb2.AudioEncoding.A_LAW  # type: ignore[attr-defined]

    def test_mu_law(self):
        assert get_audio_encoding("mu-law") == techmo_tts_pb2.AudioEncoding.MU_LAW  # type: ignore[attr-defined]

    def test_unknown_encoding_raises(self):
        with pytest.raises(RuntimeError, match="Unsupported audio-encoding"):
            get_audio_encoding("mp3")


class TestCreateOutPath:
    def test_explicit_path_returned_unchanged(self):
        enc = techmo_tts_pb2.AudioEncoding.PCM16  # type: ignore[attr-defined]
        assert create_out_path("/tmp/my.wav", enc) == "/tmp/my.wav"  # noqa: S108

    def test_empty_path_pcm16_gives_wav(self):
        enc = techmo_tts_pb2.AudioEncoding.PCM16  # type: ignore[attr-defined]
        assert create_out_path("", enc) == "output.wav"

    def test_empty_path_a_law_gives_wav(self):
        enc = techmo_tts_pb2.AudioEncoding.A_LAW  # type: ignore[attr-defined]
        assert create_out_path("", enc) == "output.wav"

    def test_empty_path_mu_law_gives_wav(self):
        enc = techmo_tts_pb2.AudioEncoding.MU_LAW  # type: ignore[attr-defined]
        assert create_out_path("", enc) == "output.wav"

    def test_empty_path_ogg_vorbis_gives_ogg(self):
        enc = techmo_tts_pb2.AudioEncoding.OGG_VORBIS  # type: ignore[attr-defined]
        assert create_out_path("", enc) == "output.ogg"

    def test_empty_path_ogg_opus_gives_ogg(self):
        enc = techmo_tts_pb2.AudioEncoding.OGG_OPUS  # type: ignore[attr-defined]
        assert create_out_path("", enc) == "output.ogg"

    def test_unsupported_encoding_raises(self):
        with pytest.raises(RuntimeError, match="Unsupported audio encoding"):
            create_out_path("", 999)


class TestCreateVoice:
    def test_name_only(self):
        voice = create_voice(voice_name="Agnieszka-1", voice_gender="", voice_age="", voice_variant=1)
        assert voice.name == "Agnieszka-1"

    def test_female_gender(self):
        voice = create_voice(voice_name="", voice_gender="female", voice_age="", voice_variant=1)
        assert voice.gender == techmo_tts_pb2.Gender.FEMALE  # type: ignore[attr-defined]

    def test_male_gender(self):
        voice = create_voice(voice_name="", voice_gender="male", voice_age="", voice_variant=1)
        assert voice.gender == techmo_tts_pb2.Gender.MALE  # type: ignore[attr-defined]

    def test_adult_age(self):
        voice = create_voice(voice_name="", voice_gender="", voice_age="adult", voice_variant=1)
        assert voice.age == techmo_tts_pb2.Age.ADULT  # type: ignore[attr-defined]

    def test_child_age(self):
        voice = create_voice(voice_name="", voice_gender="", voice_age="child", voice_variant=1)
        assert voice.age == techmo_tts_pb2.Age.CHILD  # type: ignore[attr-defined]

    def test_senile_age(self):
        voice = create_voice(voice_name="", voice_gender="", voice_age="senile", voice_variant=1)
        assert voice.age == techmo_tts_pb2.Age.SENILE  # type: ignore[attr-defined]

    def test_variant(self):
        voice = create_voice(voice_name="", voice_gender="", voice_age="", voice_variant=3)
        assert voice.variant == 3

    def test_unsupported_gender_raises(self):
        with pytest.raises(RuntimeError, match="Unsupported voice-gender"):
            create_voice(voice_name="", voice_gender="nonbinary", voice_age="", voice_variant=1)

    def test_unsupported_age_raises(self):
        with pytest.raises(RuntimeError, match="Unsupported voice-age"):
            create_voice(voice_name="", voice_gender="", voice_age="toddler", voice_variant=1)


class TestPrepareSynthesisConfig:
    def test_all_defaults_returns_none(self):
        result = prepare_synthesis_config(
            language_code="",
            voice_name="",
            voice_age="",
            voice_gender="",
            voice_variant=1,
            speech_pitch=1.0,
            speech_range=1.0,
            speech_rate=1.0,
            speech_stress=1.0,
            speech_volume=1.0,
        )
        assert result is None

    def test_language_code_returns_config(self):
        result = prepare_synthesis_config(
            language_code="pl-PL",
            voice_name="",
            voice_age="",
            voice_gender="",
            voice_variant=1,
            speech_pitch=1.0,
            speech_range=1.0,
            speech_rate=1.0,
            speech_stress=1.0,
            speech_volume=1.0,
        )
        assert result is not None
        assert result.language_code == "pl-PL"

    def test_voice_name_triggers_voice_in_config(self):
        result = prepare_synthesis_config(
            language_code="",
            voice_name="Agnieszka-1",
            voice_age="",
            voice_gender="",
            voice_variant=1,
            speech_pitch=1.0,
            speech_range=1.0,
            speech_rate=1.0,
            speech_stress=1.0,
            speech_volume=1.0,
        )
        assert result is not None
        assert result.voice.name == "Agnieszka-1"

    def test_non_default_speech_rate_sets_prosodic(self):
        result = prepare_synthesis_config(
            language_code="",
            voice_name="",
            voice_age="",
            voice_gender="",
            voice_variant=1,
            speech_pitch=1.0,
            speech_range=1.0,
            speech_rate=1.5,
            speech_stress=1.0,
            speech_volume=1.0,
        )
        assert result is not None
        assert abs(result.prosodic_properties.rate - 1.5) < 1e-6

    def test_non_default_variant_triggers_voice(self):
        result = prepare_synthesis_config(
            language_code="",
            voice_name="",
            voice_age="",
            voice_gender="",
            voice_variant=2,
            speech_pitch=1.0,
            speech_range=1.0,
            speech_rate=1.0,
            speech_stress=1.0,
            speech_volume=1.0,
        )
        assert result is not None
        assert result.voice.variant == 2
