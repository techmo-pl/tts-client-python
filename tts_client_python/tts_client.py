from __future__ import annotations

import argparse
import codecs
import os
import re
import sys
import textwrap
from collections.abc import Sequence
from typing import Any

import tts_client_python.general as general
import tts_client_python.lexicons as lexicons
import tts_client_python.recordings as recordings
from tts_client_python.VERSION import TTS_CLIENT_PYTHON_VERSION

legal_header = textwrap.dedent(
    f"""
    Techmo TTS Client, version {TTS_CLIENT_PYTHON_VERSION}
    Copyright (C) 2026 Techmo sp. z o.o.
    """
)


def check_voice_parameters(voice_name: str, language_code: str) -> None:
    if voice_name == "":
        print("No voice name provided!")
        sys.exit(1)
    if language_code == "":
        print("No voice language_code provided!")
        sys.exit(1)


class Once(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error("argument {}: allowed once".format("/".join(self.option_strings)))
        setattr(namespace, self.dest, values)


def ensure_int(value: str) -> int:
    try:
        int_value = int(value)
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"invalid int value: '{value}'") from err
    else:
        return int_value


def positive_int(value: str) -> int:
    int_value = ensure_int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            f"must be greater than 0: '{value}'",
        )
    return int_value


def unsigned_int(value: str) -> int:
    int_value = ensure_int(value)
    if int_value < 0:
        raise argparse.ArgumentTypeError(
            f"must be greater than or equal to 0: '{value}'",
        )
    return int_value


def valid_tls_dir(value: str) -> str:
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"Invalid directory path: '{value}'")

    required_files = ["client.crt", "client.key", "ca.crt"]
    missing_files = [f for f in required_files if not os.path.isfile(os.path.join(value, f))]
    if missing_files:
        raise argparse.ArgumentTypeError(f"There are missing files in tls-dir {value}: {', '.join(missing_files)}")
    return value


def valid_session_id(value: str | None) -> str:
    if value is None:
        return ""
    if not re.match(r"^[0-9a-zA-Z_-]+$", value):
        raise argparse.ArgumentTypeError(f"Invalid session ID format: '{value}'")
    if len(value) >= 64:
        raise argparse.ArgumentTypeError("Session ID is too long (must be shorter than 64 characters)")
    return value


def valid_service_address(value: str) -> str:
    if not re.match(r"^([a-zA-Z0-9.-]+):([0-9]{1,5})$", value):
        raise argparse.ArgumentTypeError(f"Invalid service address format: '{value}'. Pass 'address:port'")
    return value


def main() -> None:
    print("Techmo TTS gRPC client " + TTS_CLIENT_PYTHON_VERSION)

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=legal_header,
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    arguments_list = parser.add_argument_group("DESCRIPTION")

    arguments_list.add_argument(
        "-h",
        "--help",
        action="help",
        help=textwrap.dedent(
            """\
            Shows this help message.
        """
        ),
    )
    arguments_list.add_argument(
        "--print-service-version",
        dest="print_service_version",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Shows the version of the specified TTS service.
        """
        ),
    )
    arguments_list.add_argument(
        "--print-resources-id",
        dest="print_resources_id",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Prints the identification string of the resources used by the service.
        """
        ),
    )
    arguments_list.add_argument(
        "-s",
        "--service-address",
        metavar="IP:PORT",
        required=True,
        action=Once,
        type=valid_service_address,
        help=textwrap.dedent(
            """\
            An IP address and a port (address:port) of a service the client should connect to.
        """
        ),
    )
    arguments_list.add_argument(
        "-t",
        "--text",
        dest="text",
        metavar="TEXT",
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            A text to be synthesized. Each synthesis request has to provide either the option `--text`
            or `--input-path` (input from a file).
        """
        ),
    )
    arguments_list.add_argument(
        "-i",
        "--input-path",
        dest="inputfile",
        metavar="INPUT_FILE",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            A path to the file with text to be synthesized. Each synthesis request has to provide either
            the option `--text` or `--input-path` (input from a file).
        """
        ),
    )
    arguments_list.add_argument(
        "-o",
        "--out-path",
        dest="out_path",
        metavar="OUT_PATH",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            A path to the output audio file with synthesized speech content.
        """
        ),
    )
    arguments_list.add_argument(
        "-l",
        "--language-code",
        dest="language_code",
        metavar="LANGUAGE_CODE",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            ISO 639-1 language code of the phrase to be synthesized (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "-r",
        "--response",
        dest="response",
        metavar="RESPONSE_TYPE",
        action=Once,
        type=str,
        default="streaming",
        choices=["streaming", "single"],
        help=textwrap.dedent(
            """\
            'streaming' or 'single', calls the streaming (default) or non-streaming version of Synthesize call.
        """
        ),
    )
    arguments_list.add_argument(
        "--tls",
        action="store_true",
        help=textwrap.dedent(
            """\
            Enables simple one-way TLS encryption, using root certificates retrieved from a default location
            chosen by gRPC runtime. Ignored if used along with other '--tls-*' options.
        """
        ),
    )
    arguments_list.add_argument(
        "--tls-dir",
        dest="tls_dir",
        metavar="arg",
        action=Once,
        type=valid_tls_dir,
        help=textwrap.dedent(
            """\
            A path to a directory containing TLS credential files.
            The encryption method depends on the directory contents:
             - ca.crt - one-way TLS with server authentication using x509 CA Certificate
             - client.crt + client.key - mutual TLS
             - client.crt + client.key + ca.crt - mutual TLS with server authentication
               using x509 CA Certificate.
            The credencial files can alternatively be provided using the options:
            '--tls-ca-cert-file', '--tls-cert-file', '--tls-private-key-file'.
        """
        ),
    )
    arguments_list.add_argument(
        "--tls-ca-cert-file",
        dest="tls_ca_cert_file",
        metavar="arg",
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            A path to the file containing x509 CA Certificate used for server authentication
            (with intermediate CA certs, if any, concatenated after CA cert).
        """
        ),
    )
    arguments_list.add_argument(
        "--tls-cert-file",
        dest="tls_cert_file",
        metavar="arg",
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            A path to file containing x509 Certificate used for client authentication. This option
            must be used along with '--tls-private-key-file'. When these two options are used,
            mutual TLS is enabled. Additionally the '--tls-ca-cert-file' option can be used to select
            x509 CA Certificate for server authentication.
        """
        ),
    )
    arguments_list.add_argument(
        "--tls-private-key-file",
        dest="tls_private_key_file",
        metavar="arg",
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            A path to the file containing x509 private key matching tls-cert-file. This option
            must be used along with '--tls-cert-file'. When these two options are used,
            mutual TLS is enabled. Additionally the '--tls-ca-cert-file' option can be used to select
            x509 CA Certificate for server authentication.
        """
        ),
    )
    arguments_list.add_argument(
        "--play",
        dest="play",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Plays synthesized audio. Works only with pcm16 (default) encoding.
        """
        ),
    )
    arguments_list.add_argument(
        "--session-id",
        dest="session_id",
        metavar="SESSION_ID",
        action=Once,
        type=valid_session_id,
        default=None,
        help=textwrap.dedent(
            """\
            A session ID to be passed to the service. If not specified, the service generates
            a default session ID based on the timestamp of the request.
        """
        ),
    )
    arguments_list.add_argument(
        "--grpc-timeout",
        dest="grpc_timeout",
        metavar="GRPC_TIMEOUT",
        action=Once,
        type=unsigned_int,
        default=0,
        help=textwrap.dedent(
            """\
            A timeout in milliseconds used to set gRPC deadline - how long the client is willing to wait
            for a reply from the server (optional).
        """
        ),
    )
    arguments_list.add_argument(
        "--sampling-rate-hz",
        dest="sampling_rate",
        metavar="SAMPLING_RATE",
        action=Once,
        type=unsigned_int,
        default=0,
        help=textwrap.dedent(
            """\
            A sampling rate in Hz of synthesized audio. Set to 0 (default) to use voice's native sampling rate.
        """
        ),
    )
    arguments_list.add_argument(
        "--ae",
        "--audio-encoding",
        dest="audio_encoding",
        metavar="ENCODING",
        action=Once,
        type=str,
        default="pcm16",
        choices=["pcm16", "ogg-vorbis", "ogg-opus", "a-law", "mu-law"],
        help=textwrap.dedent(
            """\
            An encoding of the output audio, pcm16 (default), 'ogg-vorbis', 'ogg-opus', 'a-law', or 'mu-law'.
        """
        ),
    )
    arguments_list.add_argument(
        "--max-frame-size",
        dest="max_frame_size",
        metavar="MAX_FRAME_SIZE",
        action=Once,
        type=unsigned_int,
        default=0,
        help=textwrap.dedent(
            """\
            Maximum frame size for RTF (Real Time Factor) throttling. Optional, 0 (default) means that
            RTF throttling is disabled.
        """
        ),
    )
    arguments_list.add_argument(
        "--speech-pitch",
        dest="speech_pitch",
        metavar="SPEECH_PITCH",
        action=Once,
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
            Allows adjusting the default pitch of the synthesized speech (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--speech-range",
        dest="speech_range",
        metavar="SPEECH_RANGE",
        action=Once,
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
            Allows adjusting the default range of the synthesized speech (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--speech-rate",
        dest="speech_rate",
        metavar="SPEECH_RATE",
        action=Once,
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
            Allows adjusting the default rate (speed) of the synthesized speech (optional, can be overridden
            by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--speech-stress",
        dest="speech_stress",
        metavar="SPEECH_STRESS",
        action=Once,
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
            Allows adjusting the default stress of the synthesized speech (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--speech-volume",
        dest="speech_volume",
        metavar="SPEECH_VOLUME",
        action=Once,
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
            Allows adjusting the default volume of the synthesized speech (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--list-voices",
        dest="list_voices",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Lists all available voices.
        """
        ),
    )
    arguments_list.add_argument(
        "--vn",
        "--voice-name",
        dest="voice_name",
        metavar="VOICE_NAME",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            A name of the voice used to synthesize the phrase (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--vg",
        "--voice-gender",
        dest="voice_gender",
        metavar="VOICE_GENDER",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            A gender of the voice - 'female' or 'male' (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--va",
        "--voice-age",
        dest="voice_age",
        metavar="VOICE_AGE",
        action=Once,
        type=str,
        default="",
        choices=["adult", "child", "senile"],
        help=textwrap.dedent(
            """\
            An age of the voice - 'adult', 'child', or 'senile' (optional, can be overridden by SSML).
        """
        ),
    )
    arguments_list.add_argument(
        "--voice-variant",
        dest="voice_variant",
        metavar="VOICE_VARIANT",
        action=Once,
        type=positive_int,
        default=1,
        help=textwrap.dedent(
            """\
            A variant of the voice - positive integer (optional, can be overridden by SSML). Default value is 1.
        """
        ),
    )
    arguments_list.add_argument(
        "--list-sound-icons",
        dest="list_sound_icons",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Lists all available sound icons for the requested voice and language. This request requires also
            arguments: '--voice-name' and '--language-code', and may optionally specify '--voice-variant'
            (if not specified, the default variant (1) is used).
        """
        ),
    )
    arguments_list.add_argument(
        "--list-recordings",
        dest="list_recordings",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Lists all available recordings for the requested voice and language. This request requires also
            arguments: '--voice-name' and '--language-code', and may optionally specify '--voice-variant'
            (if not specified, the default variant (1) is used).
        """
        ),
    )
    arguments_list.add_argument(
        "--get-recording",
        nargs=2,
        metavar=("RECORDING_KEY", "OUTPUT_PATH"),
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            Sends back the recording with the requested key for the requested voice in the linear PCM16 format.
            This request requires also arguments: '--voice-name' and '--language-code', and may optionally specify
            '--voice-variant' (if not specified, the default variant (1) is used).
        """
        ),
    )
    arguments_list.add_argument(
        "--put-recording",
        nargs=2,
        metavar=("RECORDING_KEY", "AUDIO_PATH"),
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            Adds a recording to the list of recordings of requested voice and language. This request requires also
            arguments: '--voice-name' and '--language-code', and may optionally specify '--voice-variant'
            (if not specified, the default variant (1) is used).
        """
        ),
    )
    arguments_list.add_argument(
        "--delete-recording",
        dest="delete_recording_key",
        metavar="RECORDING_KEY",
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            Deletes the recording from the list of recordings of requested voice and language. This request requires
            also arguments: '--voice-name' and '--language-code', and may optionally specify '--voice-variant'
            (if not specified, the default variant (1) is used).
        """
        ),
    )
    arguments_list.add_argument(
        "--list-lexicons",
        dest="list_lexicons",
        action="store_true",
        default=False,
        help=textwrap.dedent(
            """\
            Lists all available pronunciation lexicons.
        """
        ),
    )
    arguments_list.add_argument(
        "--get-lexicon",
        nargs=2,
        metavar=("LEXICON_URI", "OUTPUT_PATH"),
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            Saves the content of the lexicon from the service-wide list of lexicons.
        """
        ),
    )
    arguments_list.add_argument(
        "--put-lexicon",
        nargs=3,
        metavar=("LEXICON_URI", "LEXICON_PATH", "OUTSIDE_LOOKUP_BEHAVIOUR"),
        action=Once,
        type=str,
        help=textwrap.dedent(
            """\
            Adds lexicon to the service-wide list of lexicons.
            - LEXICON_URI - a custom string identifying a given lexicon at the service level.
            - LEXICON_PATH - path to the lexicon file.
            - OUTSIDE_LOOKUP_BEHAVIOUR - 'allowed' (the service uses the lexicon outside the SSML <lookup> tag) or
            'disallowed'.
        """
        ),
    )
    arguments_list.add_argument(
        "--delete-lexicon",
        dest="lexicon_to_delete",
        metavar="LEXICON_URI",
        action=Once,
        type=str,
        default="",
        help=textwrap.dedent(
            """\
            Deletes lexicon from the service-wide list of lexicons.
        """
        ),
    )

    # Parse and validate options
    args = parser.parse_args()

    # Check if service address and port are provided
    if len(args.service_address) == 0:
        raise RuntimeError("No service address and port provided.")

    if (args.tls) and (
        (args.tls_dir is not None) or (args.tls_ca_cert_file is not None) or (args.tls_private_key_file is not None) or (args.tls_cert_file is not None)
    ):
        raise ValueError("--tls flag cannot be used along with the other --tls-* options.")

    if (args.tls_private_key_file is not None) and (args.tls_cert_file is None):
        raise ValueError("The '--tls-private-key-file' option requires the use of '--tls-cert-file'.")

    if (args.tls_cert_file is not None) and (args.tls_private_key_file is None):
        raise ValueError("The '--tls-cert-file' option requires the use of '--tls-private-key-file'.")

    if args.print_service_version:
        general.print_service_version(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
        )
        sys.exit(0)

    if args.print_resources_id:
        general.print_resources_id(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
        )
        sys.exit(0)

    if args.list_voices:
        general.list_voices(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
        )
        sys.exit(0)

    if args.list_sound_icons:
        check_voice_parameters(args.voice_name, args.language_code)
        recordings.list_sound_icons(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
            voice_name=args.voice_name,
            voice_variant=args.voice_variant,
        )
        sys.exit(0)

    if args.list_recordings:
        check_voice_parameters(args.voice_name, args.language_code)
        recordings.list_recordings(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
            voice_name=args.voice_name,
            voice_variant=args.voice_variant,
        )
        sys.exit(0)

    if args.get_recording is not None:
        check_voice_parameters(args.voice_name, args.language_code)
        recordings.get_recording(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
            voice_name=args.voice_name,
            voice_variant=args.voice_variant,
            recording_key=args.get_recording[0],
            output_path=args.get_recording[1],
        )
        sys.exit(0)

    if args.put_recording is not None:
        check_voice_parameters(args.voice_name, args.language_code)
        recordings.put_recording(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
            voice_name=args.voice_name,
            voice_variant=args.voice_variant,
            recording_key=args.put_recording[0],
            audio_path=args.put_recording[1],
        )
        sys.exit(0)

    if args.delete_recording_key is not None:
        check_voice_parameters(args.voice_name, args.language_code)
        recordings.delete_recording(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
            voice_name=args.voice_name,
            voice_variant=args.voice_variant,
            recording_key=args.delete_recording_key,
        )
        sys.exit(0)

    if args.list_lexicons:
        lexicons.list_lexicons(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            language_code=args.language_code,
        )
        sys.exit(0)

    if args.get_lexicon is not None:
        lexicons.get_lexicon(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            lexicon_uri=args.get_lexicon[0],
            output_path=args.get_lexicon[1],
        )
        sys.exit(0)

    if args.put_lexicon is not None:
        lexicons.put_lexicon(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            lexicon_uri=args.put_lexicon[0],
            lexicon_path=args.put_lexicon[1],
            outside_lookup_behaviour=args.put_lexicon[2],
        )
        sys.exit(0)

    if args.lexicon_to_delete != "":
        lexicons.delete_lexicon(
            service_address=args.service_address,
            tls=args.tls,
            tls_dir=args.tls_dir,
            tls_ca_cert_file=args.tls_ca_cert_file,
            tls_cert_file=args.tls_cert_file,
            tls_private_key_file=args.tls_private_key_file,
            session_id=args.session_id,
            grpc_timeout=args.grpc_timeout,
            lexicon_uri=args.lexicon_to_delete,
        )
        sys.exit(0)

    # Input text determination
    if args.inputfile != "":
        with codecs.open(args.inputfile, encoding="utf-8", mode="r") as fread:
            input_text = fread.read()
    elif args.text != "":
        input_text = args.text
    else:
        print("Empty input string for synthesis. Use --text or --input-path to provide text.")
        parser.print_help()
        sys.exit(1)

    general.synthesize(
        service_address=args.service_address,
        tls=args.tls,
        tls_dir=args.tls_dir,
        tls_ca_cert_file=args.tls_ca_cert_file,
        tls_cert_file=args.tls_cert_file,
        tls_private_key_file=args.tls_private_key_file,
        session_id=args.session_id,
        grpc_timeout=args.grpc_timeout,
        audio_encoding=args.audio_encoding,
        sampling_rate=args.sampling_rate,
        max_frame_size=args.max_frame_size,
        language_code=args.language_code,
        voice_name=args.voice_name,
        voice_age=args.voice_age,
        voice_gender=args.voice_gender,
        voice_variant=args.voice_variant,
        speech_pitch=args.speech_pitch,
        speech_range=args.speech_range,
        speech_rate=args.speech_rate,
        speech_stress=args.speech_stress,
        speech_volume=args.speech_volume,
        play=args.play,
        response=args.response,
        out_path=args.out_path,
        text=input_text,
    )


if __name__ == "__main__":
    main()
