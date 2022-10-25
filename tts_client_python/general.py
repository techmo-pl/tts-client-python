from tts_client_python.proto import techmo_tts_pb2 as techmo_tts_pb2
from tts_client_python.proto import techmo_tts_pb2_grpc as techmo_tts_pb2_grpc
from io import BytesIO
import grpc
import os
import wave
import struct
import sys
import numpy as np
import sounddevice as sd


class AudioPlayer:
    def __init__(self, sampling_rate_hz=None, encoding="pcm16"):
        self.sampling_rate_hz = sampling_rate_hz
        self.stream = None

        if encoding == "pcm16":
            self.encoding = np.int16
        elif encoding == "ogg-vorbis":
            raise RuntimeError("OGG-Vorbis audio-encoding is not implemented.")
        else:
            raise RuntimeError("Unsupported audio-encoding: " + str(encoding))

    def start(self, sampling_rate_hz=None):
        if sampling_rate_hz is not None:
            self.sampling_rate_hz = sampling_rate_hz
        self.stop()
        self.stream = sd.OutputStream(
            samplerate=self.sampling_rate_hz,
            blocksize=1024,
            channels=1,
            dtype=self.encoding,
        )
        self.stream.start()

    def append(self, audio):
        self.stream.write(np.fromstring(audio, dtype=np.int16))

    def stop(self):
        if self.stream is not None:
            self.stream.close()


class AudioSaver:
    """Wave Saver for TTS"""

    _buffer = None
    _framerate = None
    _nchannels = None
    _sampwidth = None
    _encoding = None

    def __init__(self, sampling_frequency=None):
        self._buffer = bytearray()
        self._framerate = sampling_frequency
        self._nchannels = 1
        self._sampwidth = 2

    def setEncoding(self, encoding):
        self._encoding = encoding

    def setFrameRate(self, sampling_frequency):
        self._framerate = sampling_frequency

    def append(self, audiodata):
        self._buffer += audiodata

    def clear(self):
        self._buffer.clear()

    def save(self, filename):
        if self._encoding == techmo_tts_pb2.AudioEncoding.PCM16:
            if not self._framerate:
                raise RuntimeError("Sample rate has not been set")
            with wave.open(filename, "w") as w:
                params = (
                    self._nchannels,
                    self._sampwidth,
                    self._framerate,
                    len(self._buffer),
                    "NONE",
                    "not compressed",
                )
                w.setparams(params)
                w.writeframes(self._buffer)
        else:
            f = open(filename, "wb")
            f.write(self._buffer)
            f.close()

    def load(self, filename):
        with wave.open(filename, "r") as wr:
            self._buffer = wr.readframes(wr.getnframes())

    def isEqualTo(self, asv):
        return self._buffer == asv._buffer

    def print(self):
        if len(self._buffer) > 0:
            header = struct.pack(
                "<4sL4s4sLHHLLHH4sL",
                b"RIFF",
                36 + len(self._buffer),
                b"WAVE",
                b"fmt ",
                16,
                0x0001,
                self._nchannels,
                self._framerate,
                self._nchannels * self._framerate * self._sampwidth,
                self._nchannels * self._sampwidth,
                self._sampwidth * 8,
                b"data",
                len(self._buffer),
            )
            sys.stdout._buffer.write(header + bytes(self.buffer))


class GrpcRequestConfig:
    _channel = None
    _stub = None
    _timeout = None
    _metadata = None

    def __init__(self, service, tls_directory, grpc_timeout, session_id):
        self._channel = create_channel(service, tls_directory)
        self._stub = techmo_tts_pb2_grpc.TTSStub(self._channel)
        if grpc_timeout > 0:
            self._timeout = grpc_timeout / 1000
        self._metadata = []
        if session_id:
            self._metadata = [("session_id", session_id)]

    def get_channel(self):
        return self._channel

    def get_stub(self):
        return self._stub

    def get_timeout(self):
        return self._timeout

    def get_metadata(self):
        return self._metadata


def list_voices(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.ListVoicesRequest(language=args.language)

    try:
        stub = rc.get_stub()
        response = stub.ListVoices(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        print("\nAvailable voices:\n")
        print(response)
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def synthesize(args, text):
    audio_encoding = get_audio_encoding(args)
    out_path = create_out_path(args, audio_encoding)

    channel = create_channel(args.service, args.tls_directory)
    stub = techmo_tts_pb2_grpc.TTSStub(channel)

    config = techmo_tts_pb2.SynthesizeConfig(
        language=args.language,
        voice=create_voice(args),
        prosodic_properties=techmo_tts_pb2.ProsodicProperties(
            pitch=args.speech_pitch,
            range=args.speech_range,
            rate=args.speech_rate,
            volume=args.speech_volume,
        ),
        audio_config=techmo_tts_pb2.AudioConfig(
            audio_encoding=audio_encoding,
            sampling_rate_hz=int(args.sample_rate),
        ),
    )

    if args.phoneme_modifiers != "":
        try:
            phoneme_modifiers_array = (
                args.phoneme_modifiers[1:-1].replace("),", ");").split(";")
            )

            for single_phoneme_modifiers_string in phoneme_modifiers_array:
                single_phoneme_modifiers = single_phoneme_modifiers_string.replace(
                    " ", ""
                )[1:-1].split(",")
                config.phoneme_modifiers.append(
                    techmo_tts_pb2.PhonemeModifiers(
                        phoneme_index=int(single_phoneme_modifiers[0]),
                        new_pitch=float(single_phoneme_modifiers[1]),
                        new_duration=float(single_phoneme_modifiers[2]),
                    )
                )
        except Exception as e:
            print(
                "Error while parsing the list of phoneme modifiers:",
                str(e),
                "\nEnsure that format of provided phoneme modifiers list is correct: [(index1, pitch1, duration1), (index2, pitch2, duration2), ...]",
            )

    request = techmo_tts_pb2.SynthesizeRequest(text=text, config=config)

    timeout = None
    if args.grpc_timeout > 0:
        timeout = args.grpc_timeout / 1000  # milliseconds to seconds
    metadata = []
    if args.session_id:
        metadata = [("session_id", args.session_id)]

    audioPlayer = None
    if args.play:
        if args.sample_rate:
            player_sampling_rate = int(args.sample_rate)
        else:
            player_sampling_rate = 8000

        audioPlayer = AudioPlayer(
            sampling_rate_hz=player_sampling_rate, encoding=args.audio_encoding
        )
    audioSaver = AudioSaver()
    audioSaver.setEncoding(audio_encoding)

    try:
        if args.response == "streaming":
            internal_synthesize_streaming(
                stub, request, timeout, metadata, audioSaver, audioPlayer
            )
        elif args.response == "single":
            internal_synthesize(
                stub, request, timeout, metadata, audioSaver, audioPlayer
            )
        else:
            raise RuntimeError("Unsupported response type: " + args.response)
        audioSaver.save(out_path)
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )
    finally:
        if args.play:
            audioPlayer.stop()
    audioSaver.clear()


def create_channel(address, tls_directory):
    if not tls_directory:
        return grpc.insecure_channel(address)

    def read_file(path):
        with open(path, "rb") as file:
            return file.read()

    return grpc.secure_channel(
        address,
        grpc.ssl_channel_credentials(
            read_file(os.path.join(tls_directory, "ca.crt")),
            read_file(os.path.join(tls_directory, "client.key")),
            read_file(os.path.join(tls_directory, "client.crt")),
        ),
    )


def create_out_path(args, audio_encoding):
    out_path = args.out_path
    if out_path == "":
        if audio_encoding == techmo_tts_pb2.AudioEncoding.PCM16:
            out_path = "TechmoTTS.wav"
        else:
            out_path = "TechmoTTS.ogg"
    return os.path.join(out_path)


def create_voice(args):
    if args.voice_name != "" or args.voice_gender != "" or args.voice_age != "":
        gender = techmo_tts_pb2.Gender.GENDER_UNSPECIFIED
        if args.voice_gender == "female":
            gender = techmo_tts_pb2.Gender.FEMALE
        elif args.voice_gender == "male":
            gender = techmo_tts_pb2.Gender.MALE
        elif args.voice_gender != "":
            raise RuntimeError("Unsupported voice-gender: " + args.voice_gender)

        age = techmo_tts_pb2.Age.AGE_UNSPECIFIED
        if args.voice_age == "adult":
            age = techmo_tts_pb2.Age.ADULT
        elif args.voice_age == "child":
            age = techmo_tts_pb2.Age.CHILD
        elif args.voice_age == "senile":
            age = techmo_tts_pb2.Age.SENILE
        elif args.voice_age != "":
            raise RuntimeError("Unsupported voice-age: " + args.voice_age)

        return techmo_tts_pb2.Voice(
            name=args.voice_name, gender=gender, age=age, variant=args.voice_variant
        )
    else:
        return None


def get_audio_encoding(args):
    if args.audio_encoding == "pcm16":
        return techmo_tts_pb2.AudioEncoding.PCM16
    elif args.audio_encoding == "ogg-vorbis":
        return techmo_tts_pb2.AudioEncoding.OGG_VORBIS
    else:
        raise RuntimeError("Unsupported audio-encoding: " + args.audio_encoding)


def internal_synthesize(stub, request, timeout, metadata, audio_saver, audio_player):
    response = stub.Synthesize(request, timeout=timeout, metadata=metadata)
    if audio_player is not None:
        audio_player.start(sample_rate=response.sampling_rate_hz)
        audio_player.append(response.audio)
    audio_saver.setFrameRate(response.sampling_rate_hz)
    audio_saver.append(response.audio)


def internal_synthesize_streaming(
    stub, request, timeout, metadata, audio_saver, audio_player
):
    if audio_player is not None:
        audio_player.start()
    for response in stub.SynthesizeStreaming(
        request, timeout=timeout, metadata=metadata
    ):
        if audio_saver._framerate:
            if audio_saver._framerate != response.sampling_rate_hz:
                raise RuntimeError("Sample rate does not match previously received.")
        else:
            audio_saver.setFrameRate(response.sampling_rate_hz)
        if audio_player is not None:
            audio_player.append(response.audio)
        audio_saver.append(response.audio)
