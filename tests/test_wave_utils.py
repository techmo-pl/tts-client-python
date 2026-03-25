"""Unit tests for write_wave_file() and AudioSaver in wave_utils.py / general.py."""

from __future__ import annotations

import struct

import pytest

from tts_client_python.general import AudioSaver
from tts_client_python.proto import techmo_tts_pb2
from tts_client_python.wave_utils import AudioFormat, write_wave_file


class TestWriteWaveFile:
    def _parse_header(self, data: bytes) -> dict:
        fmt = "<4sL4s4sLHHLLHH4sL"
        header_size = struct.calcsize(fmt)
        (
            riff,
            riff_size,
            wave,
            fmt_id,
            fmt_chunk_size,
            audio_fmt,
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            data_id,
            data_size,
        ) = struct.unpack(fmt, data[:header_size])
        return {
            "riff": riff,
            "riff_size": riff_size,
            "wave": wave,
            "fmt_id": fmt_id,
            "fmt_chunk_size": fmt_chunk_size,
            "audio_fmt": audio_fmt,
            "num_channels": num_channels,
            "sample_rate": sample_rate,
            "byte_rate": byte_rate,
            "block_align": block_align,
            "bits_per_sample": bits_per_sample,
            "data_id": data_id,
            "data_size": data_size,
        }

    def test_riff_header_markers(self, tmp_path):
        out = tmp_path / "out.wav"
        audio_data = bytearray(b"\x00\x01" * 100)
        write_wave_file(str(out), audio_data, 16000, 1, 2, int(AudioFormat.PCM16))
        raw = out.read_bytes()
        hdr = self._parse_header(raw)
        assert hdr["riff"] == b"RIFF"
        assert hdr["wave"] == b"WAVE"
        assert hdr["fmt_id"] == b"fmt "
        assert hdr["data_id"] == b"data"

    def test_pcm16_audio_format_field(self, tmp_path):
        out = tmp_path / "out.wav"
        write_wave_file(str(out), bytearray(b"\x00" * 4), 8000, 1, 2, int(AudioFormat.PCM16))
        hdr = self._parse_header(out.read_bytes())
        assert hdr["audio_fmt"] == 1  # PCM16

    def test_a_law_audio_format_field(self, tmp_path):
        out = tmp_path / "out.wav"
        write_wave_file(str(out), bytearray(b"\x00" * 4), 8000, 1, 1, int(AudioFormat.A_LAW))
        hdr = self._parse_header(out.read_bytes())
        assert hdr["audio_fmt"] == 6

    def test_mu_law_audio_format_field(self, tmp_path):
        out = tmp_path / "out.wav"
        write_wave_file(str(out), bytearray(b"\x00" * 4), 8000, 1, 1, int(AudioFormat.MU_LAW))
        hdr = self._parse_header(out.read_bytes())
        assert hdr["audio_fmt"] == 7

    def test_data_appended_after_header(self, tmp_path):
        out = tmp_path / "out.wav"
        audio_data = bytearray(b"\xab\xcd" * 50)
        write_wave_file(str(out), audio_data, 16000, 1, 2, int(AudioFormat.PCM16))
        raw = out.read_bytes()
        header_size = struct.calcsize("<4sL4s4sLHHLLHH4sL")
        assert raw[header_size:] == bytes(audio_data)

    def test_riff_size_is_36_plus_data(self, tmp_path):
        out = tmp_path / "out.wav"
        audio_data = bytearray(b"\x00" * 200)
        write_wave_file(str(out), audio_data, 16000, 1, 2, int(AudioFormat.PCM16))
        hdr = self._parse_header(out.read_bytes())
        assert hdr["riff_size"] == 36 + len(audio_data)

    def test_sample_rate_in_header(self, tmp_path):
        out = tmp_path / "out.wav"
        write_wave_file(str(out), bytearray(b"\x00" * 4), 44100, 1, 2, int(AudioFormat.PCM16))
        hdr = self._parse_header(out.read_bytes())
        assert hdr["sample_rate"] == 44100


class TestAudioSaver:
    def test_append_accumulates_data(self):
        saver = AudioSaver()
        saver.append(b"\x01\x02")
        saver.append(b"\x03\x04")
        assert saver._buffer == bytearray(b"\x01\x02\x03\x04")

    def test_clear_empties_buffer(self):
        saver = AudioSaver()
        saver.append(b"\x01\x02")
        saver.clear()
        assert len(saver._buffer) == 0

    def test_save_pcm16_writes_wav(self, tmp_path):
        saver = AudioSaver(sampling_frequency=16000)
        saver.setEncoding(techmo_tts_pb2.AudioEncoding.PCM16)  # type: ignore[attr-defined]
        saver.append(b"\x00\x01" * 100)
        out = tmp_path / "speech.wav"
        saver.save(str(out))
        assert out.exists()
        content = out.read_bytes()
        assert content[:4] == b"RIFF"

    def test_save_ogg_writes_raw(self, tmp_path):
        saver = AudioSaver()
        saver.setEncoding(techmo_tts_pb2.AudioEncoding.OGG_VORBIS)  # type: ignore[attr-defined]
        raw = b"OggS\x00fake-ogg-data"
        saver.append(raw)
        out = tmp_path / "speech.ogg"
        saver.save(str(out))
        assert out.read_bytes() == raw

    def test_save_without_framerate_raises(self, tmp_path):
        saver = AudioSaver()
        saver.setEncoding(techmo_tts_pb2.AudioEncoding.PCM16)  # type: ignore[attr-defined]
        saver.append(b"\x00\x01")
        with pytest.raises(RuntimeError, match="Sample rate has not been set"):
            saver.save(str(tmp_path / "out.wav"))

    def test_set_frame_rate_and_samp_width(self):
        saver = AudioSaver()
        saver.setFrameRate(8000)
        saver.setSampWidth(1)
        assert saver._framerate == 8000
        assert saver._sampwidth == 1

    def test_is_equal_to(self):
        saver1 = AudioSaver()
        saver2 = AudioSaver()
        saver1.append(b"\xaa\xbb")
        saver2.append(b"\xaa\xbb")
        assert saver1.isEqualTo(saver2)

    def test_is_not_equal_to(self):
        saver1 = AudioSaver()
        saver2 = AudioSaver()
        saver1.append(b"\xaa")
        saver2.append(b"\xbb")
        assert not saver1.isEqualTo(saver2)
