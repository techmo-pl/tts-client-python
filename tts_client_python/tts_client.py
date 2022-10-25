from argparse import ArgumentParser
import codecs
from tts_client_python.VERSION import TTS_CLIENT_PYTHON_VERSION
import tts_client_python.general as general
import tts_client_python.lexicons as lexicons
import tts_client_python.recordings as recordings


def main():
    print("Techmo TTS gRPC client " + TTS_CLIENT_PYTHON_VERSION)

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--service-address",
        dest="service",
        metavar="IP:PORT",
        required=True,
        help="An IP address and port (address:port) of a service the client connects to.",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--text",
        dest="text",
        metavar="TEXT",
        default="Polski tekst do syntezy",
        help="A text to be synthesized.",
        type=str,
    )
    parser.add_argument(
        "-i",
        "--input-text-file",
        dest="inputfile",
        metavar="INPUT_FILE",
        default="",
        help="A file with text to be synthesized.",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--out-path",
        dest="out_path",
        metavar="OUT_PATH",
        default="",
        help="A path to the output wave file with synthesized audio content.",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--response",
        dest="response",
        metavar="RESPONSE_TYPE",
        default="streaming",
        help='"streaming" or "single", calls the streaming (default) or non-streaming version of Synthesize.',
        type=str,
    )
    parser.add_argument(
        "--sp",
        "--speech-pitch",
        dest="speech_pitch",
        metavar="SPEECH_PITCH",
        default=1.0,
        help="Allows adjusting the default pitch of the synthesized speech (optional, can be overridden by SSML).",
        type=float,
    )
    parser.add_argument(
        "--sr",
        "--speech-range",
        dest="speech_range",
        metavar="SPEECH_RANGE",
        default=1.0,
        help="Allows adjusting the default range of the synthesized speech (optional, can be overridden by SSML).",
        type=float,
    )
    parser.add_argument(
        "--ss",
        "--speech-rate",
        dest="speech_rate",
        metavar="SPEECH_RATE",
        default=1.0,
        help="Allows adjusting the default rate (speed) of the synthesized speech (optional, can be overridden by SSML).",
        type=float,
    )
    parser.add_argument(
        "--sv",
        "--speech-volume",
        dest="speech_volume",
        metavar="SPEECH_VOLUME",
        default=1.0,
        help="Allows adjusting the default volume of the synthesized speech (optional, can be overridden by SSML).",
        type=float,
    )
    parser.add_argument(
        "--sample-rate",
        dest="sample_rate",
        metavar="SAMPLE_RATE",
        default=0,
        help="A sample rate in Hz of synthesized audio. Set to 0 (default) to use voice's original sample rate.",
        type=int,
    )
    parser.add_argument(
        "--ae",
        "--audio-encoding",
        dest="audio_encoding",
        metavar="ENCODING",
        default="pcm16",
        help="An encoding of the output audio, pcm16 (default) or ogg-vorbis.",
        type=str,
    )
    parser.add_argument(
        "--play",
        dest="play",
        default=False,
        action="store_true",
        help="Play synthesized audio. Works only with pcm16 (default) encoding.",
    )
    parser.add_argument(
        "--phoneme-modifiers",
        dest="phoneme_modifiers",
        metavar="PHONEME_MODIFIERS",
        default="",
        help="An array of additional phoneme modifiers: [(index1, pitch1, duration1), ...] for fine-tuning the output audio (optional).",
        type=str,
    )
    parser.add_argument(
        "--session-id",
        dest="session_id",
        metavar="SESSION_ID",
        default="",
        help="A session ID to be passed to the service. If not specified, the service generates a default session ID.",
        type=str,
    )
    parser.add_argument(
        "--tls-dir",
        dest="tls_directory",
        metavar="TLS_DIR",
        default="",
        help="If set to a path with SSL/TLS credential files (client.crt, client.key, ca.crt), use SSL/TLS authentication. Otherwise use insecure channel (default).",
        type=str,
    )
    parser.add_argument(
        "--grpc-timeout",
        dest="grpc_timeout",
        metavar="GRPC_TIMEOUT",
        default=0,
        help="A timeout in milliseconds used to set gRPC deadline - how long the client is willing to wait for a reply from the server (optional).",
        type=int,
    )
    parser.add_argument(
        "--list-voices",
        dest="list_voices",
        action="store_true",
        default=False,
        help="Lists all available voices.",
    )
    parser.add_argument(
        "-l",
        "--language",
        dest="language",
        metavar="LANGUAGE",
        default="",
        help="Language (ISO 639-1 code) of the voice to be used (optional, can be overridden by SSML).",
        type=str,
    )
    parser.add_argument(
        "--vn",
        "--voice-name",
        dest="voice_name",
        metavar="VOICE_NAME",
        default="",
        help="A name of the voice to be used (optional, can be overridden by SSML).",
        type=str,
    )
    parser.add_argument(
        "--vg",
        "--voice-gender",
        dest="voice_gender",
        metavar="VOICE_GENDER",
        default="",
        help="A gender of the voice to be used. Allowed values: 'female', 'male' (optional, can be overridden by SSML).",
        type=str,
    )
    parser.add_argument(
        "--va",
        "--voice-age",
        dest="voice_age",
        metavar="VOICE_AGE",
        default="",
        help="An age of the voice to be used. Allowed values: 'adult', 'child', 'senile' (optional, can be overridden by SSML).",
        type=str,
    )
    parser.add_argument(
        "--voice-variant",
        dest="voice_variant",
        metavar="VOICE_VARIANT",
        default=0,
        help="A variant of the selected voice - unsigned integer (optional, can be overriden by SSML).",
        type=int,
    )
    parser.add_argument(
        "--list-recordings",
        dest="voice_to_list_recordings_for",
        metavar="VOICE_NAME",
        default="",
        help="Lists all recording keys for the requested voice.",
        type=str,
    )
    parser.add_argument(
        "--get-recording",
        nargs=3,
        metavar=("VOICE_NAME", "RECORDING_KEY", "OUTPUT_PATH"),
        help="Sends back the recording with the requested key for the requested voice in the linear PCM16 format.",
        type=str,
    )
    parser.add_argument(
        "--put-recording",
        nargs=3,
        metavar=("VOICE_NAME", "RECORDING_KEY", "AUDIO_PATH"),
        help="Adds a new recording with the requested key for the requested voice, or overwrites the existing one if there is already such a key defined. The recording has to be PCM16 WAV audio.",
        type=str,
    )
    parser.add_argument(
        "--delete-recording",
        nargs=2,
        metavar=("VOICE_NAME", "RECORDING_KEY"),
        help="Removes the recording with the requested key from the list of recordings of the requested voice.",
        type=str,
    )
    parser.add_argument(
        "--list-lexicons",
        dest="list_lexicons",
        action="store_true",
        default=False,
        help="Lists all available lexicons.",
    )
    parser.add_argument(
        "--get-lexicon",
        dest="lexicon_to_get",
        metavar="LEXICON_NAME",
        default="",
        help="Sends back the content of the lexicon with the requested name.",
        type=str,
    )
    parser.add_argument(
        "--put-lexicon",
        nargs=2,
        metavar=("LEXICON_NAME", "LEXICON_CONTENT"),
        help="Adds a new lexicon with the requested name or overwrites the existing one if there is already a lexicon with such name. Content of the lexicon shall comply to W3C Pronunciation Lexicon Specification 1.0 (https://www.w3.org/TR/pronunciation-lexicon/).",
        type=str,
    )
    parser.add_argument(
        "--delete-lexicon",
        dest="lexicon_to_delete",
        metavar="LEXICON_NAME",
        default="",
        help="Removes the lexicon with the requested name.",
        type=str,
    )

    # Parse and validate options
    args = parser.parse_args()

    # Check if service address and port are provided
    if len(args.service) == 0:
        raise RuntimeError("No service address and port provided.")

    if args.list_voices:
        general.list_voices(args)
        return

    if args.list_lexicons:
        lexicons.list_lexicons(args)
        return

    if args.lexicon_to_get != "":
        lexicons.get_lexicon(args)
        return

    if args.put_lexicon != None:
        lexicons.put_lexicon(args)
        return

    if args.lexicon_to_delete != "":
        lexicons.delete_lexicon(args)
        return

    if args.voice_to_list_recordings_for != "":
        recordings.list_recordings(args)
        return

    if args.get_recording != None:
        recordings.get_recording(args)
        return

    if args.put_recording != None:
        recordings.put_recording(args)
        return

    if args.delete_recording != None:
        recordings.delete_recording(args)
        return

    # Input text determination
    input_text = ""
    if len(args.inputfile) > 0:
        with codecs.open(args.inputfile, encoding="utf-8", mode="r") as fread:
            input_text = fread.read()
    elif len(args.text) > 0:
        input_text = args.text
    else:
        raise RuntimeError("Empty input string for synthesis.")

    general.synthesize(args, input_text)


if __name__ == "__main__":
    main()
