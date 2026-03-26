"""Unit tests for CLI argument validation functions in tts_client.py."""

from __future__ import annotations

import argparse

import pytest

from tts_client_python.tts_client import (
    Once,
    check_voice_parameters,
    positive_int,
    unsigned_int,
    valid_service_address,
    valid_session_id,
    valid_tls_dir,
)


class TestValidServiceAddress:
    def test_valid_hostname_and_port(self):
        assert valid_service_address("dragon:45936") == "dragon:45936"

    def test_valid_ip_and_port(self):
        assert valid_service_address("192.168.1.1:8080") == "192.168.1.1:8080"

    def test_valid_localhost(self):
        assert valid_service_address("localhost:50051") == "localhost:50051"

    def test_missing_port_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid service address"):
            valid_service_address("dragon")

    def test_missing_host_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            valid_service_address(":45936")

    def test_invalid_characters_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            valid_service_address("dragon:port_abc")

    def test_port_too_long_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            valid_service_address("dragon:123456")


class TestValidSessionId:
    def test_valid_alphanumeric(self):
        assert valid_session_id("session123") == "session123"

    def test_valid_with_dash_and_underscore(self):
        assert valid_session_id("my-session_01") == "my-session_01"

    def test_none_returns_empty_string(self):
        assert valid_session_id(None) == ""

    def test_special_characters_raise(self):
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid session ID"):
            valid_session_id("invalid session!")

    def test_too_long_raises(self):
        long_id = "a" * 64
        with pytest.raises(argparse.ArgumentTypeError, match="shorter than 64"):
            valid_session_id(long_id)

    def test_exactly_63_chars_is_valid(self):
        ok_id = "a" * 63
        assert valid_session_id(ok_id) == ok_id


class TestValidTlsDir:
    def test_valid_dir_with_all_files(self, tmp_path):
        for fname in ["client.crt", "client.key", "ca.crt"]:
            (tmp_path / fname).write_bytes(b"dummy")
        assert valid_tls_dir(str(tmp_path)) == str(tmp_path)

    def test_missing_file_raises(self, tmp_path):
        (tmp_path / "client.crt").write_bytes(b"dummy")
        (tmp_path / "client.key").write_bytes(b"dummy")
        # ca.crt missing
        with pytest.raises(argparse.ArgumentTypeError, match="missing files"):
            valid_tls_dir(str(tmp_path))

    def test_nonexistent_dir_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid directory"):
            valid_tls_dir("/nonexistent/path/xyz")


class TestPositiveInt:
    def test_positive_value(self):
        assert positive_int("5") == 5

    def test_zero_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="greater than 0"):
            positive_int("0")

    def test_negative_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            positive_int("-1")

    def test_non_integer_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="invalid int"):
            positive_int("abc")


class TestUnsignedInt:
    def test_positive_value(self):
        assert unsigned_int("10") == 10

    def test_zero_is_valid(self):
        assert unsigned_int("0") == 0

    def test_negative_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="greater than or equal to 0"):
            unsigned_int("-1")

    def test_non_integer_raises(self):
        with pytest.raises(argparse.ArgumentTypeError, match="invalid int"):
            unsigned_int("3.14")


class TestCheckVoiceParameters:
    def test_valid_parameters_no_exit(self):
        check_voice_parameters("Agnieszka-1", "pl-PL")

    def test_empty_voice_name_exits(self):
        with pytest.raises(SystemExit):
            check_voice_parameters("", "pl-PL")

    def test_empty_language_code_exits(self):
        with pytest.raises(SystemExit):
            check_voice_parameters("Agnieszka-1", "")


class TestOnceAction:
    def _make_parser_with_once(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--foo", action=Once, default=None)
        return parser

    def test_single_use_succeeds(self):
        parser = self._make_parser_with_once()
        args = parser.parse_args(["--foo", "bar"])
        assert args.foo == "bar"

    def test_duplicate_use_raises_system_exit(self):
        parser = self._make_parser_with_once()
        with pytest.raises(SystemExit):
            parser.parse_args(["--foo", "a", "--foo", "b"])
