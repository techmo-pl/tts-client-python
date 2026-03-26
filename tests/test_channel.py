"""Unit tests for create_channel() branching logic in general.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tts_client_python.general import create_channel


class TestCreateChannelInsecure:
    def test_no_tls_params_creates_insecure(self):
        with patch("tts_client_python.general.grpc.insecure_channel") as mock_insecure:
            mock_insecure.return_value = MagicMock()
            create_channel(
                service_address="dragon:45936",
                tls=False,
                tls_dir="",
                tls_ca_cert_file="",
                tls_cert_file="",
                tls_private_key_file="",
            )
            mock_insecure.assert_called_once_with("dragon:45936")

    def test_no_tls_params_does_not_create_secure(self):
        with patch("tts_client_python.general.grpc.insecure_channel", return_value=MagicMock()):
            with patch("tts_client_python.general.grpc.secure_channel") as mock_secure:
                create_channel(
                    service_address="localhost:50051",
                    tls=False,
                    tls_dir="",
                    tls_ca_cert_file="",
                    tls_cert_file="",
                    tls_private_key_file="",
                )
                mock_secure.assert_not_called()


class TestCreateChannelTlsFlag:
    def test_tls_flag_true_creates_secure_channel(self):
        with patch("tts_client_python.general.grpc.secure_channel") as mock_secure:
            with patch("tts_client_python.general.grpc.ssl_channel_credentials") as mock_creds:
                mock_creds.return_value = MagicMock()
                mock_secure.return_value = MagicMock()
                create_channel(
                    service_address="dragon:45936",
                    tls=True,
                    tls_dir="",
                    tls_ca_cert_file="",
                    tls_cert_file="",
                    tls_private_key_file="",
                )
                mock_secure.assert_called_once()
                mock_creds.assert_called_once_with(None, None, None)


class TestCreateChannelTlsDir:
    def test_tls_dir_reads_cert_files(self, tmp_path):
        ca = tmp_path / "ca.crt"
        key = tmp_path / "client.key"
        crt = tmp_path / "client.crt"
        ca.write_bytes(b"ca-data")
        key.write_bytes(b"key-data")
        crt.write_bytes(b"crt-data")

        with patch("tts_client_python.general.grpc.secure_channel") as mock_secure:
            with patch("tts_client_python.general.grpc.ssl_channel_credentials") as mock_creds:
                mock_creds.return_value = MagicMock()
                mock_secure.return_value = MagicMock()
                create_channel(
                    service_address="dragon:45936",
                    tls=False,
                    tls_dir=str(tmp_path),
                    tls_ca_cert_file="",
                    tls_cert_file="",
                    tls_private_key_file="",
                )
                mock_creds.assert_called_once_with(b"ca-data", b"key-data", b"crt-data")
                mock_secure.assert_called_once()


class TestCreateChannelIndividualFiles:
    def test_individual_cert_files_override(self, tmp_path):
        ca_file = tmp_path / "ca.crt"
        ca_file.write_bytes(b"ca-content")

        with patch("tts_client_python.general.grpc.secure_channel") as mock_secure:
            with patch("tts_client_python.general.grpc.ssl_channel_credentials") as mock_creds:
                mock_creds.return_value = MagicMock()
                mock_secure.return_value = MagicMock()
                create_channel(
                    service_address="dragon:45936",
                    tls=False,
                    tls_dir="",
                    tls_ca_cert_file=str(ca_file),
                    tls_cert_file="",
                    tls_private_key_file="",
                )
                mock_creds.assert_called_once_with(b"ca-content", None, None)

    def test_mutual_tls_with_individual_files(self, tmp_path):
        ca_file = tmp_path / "ca.crt"
        cert_file = tmp_path / "client.crt"
        key_file = tmp_path / "client.key"
        ca_file.write_bytes(b"ca")
        cert_file.write_bytes(b"cert")
        key_file.write_bytes(b"key")

        with patch("tts_client_python.general.grpc.secure_channel") as mock_secure:
            with patch("tts_client_python.general.grpc.ssl_channel_credentials") as mock_creds:
                mock_creds.return_value = MagicMock()
                mock_secure.return_value = MagicMock()
                create_channel(
                    service_address="dragon:45936",
                    tls=False,
                    tls_dir="",
                    tls_ca_cert_file=str(ca_file),
                    tls_cert_file=str(cert_file),
                    tls_private_key_file=str(key_file),
                )
                mock_creds.assert_called_once_with(b"ca", b"key", b"cert")
