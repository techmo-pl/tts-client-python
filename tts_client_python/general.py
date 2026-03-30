from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

import grpc
import numpy as np
import sounddevice as sd

from techmo.tts.api.v3 import techmo_tts_pb2
from techmo.tts.api.v3 import techmo_tts_pb2_grpc
from tts_client_python.wave_utils import AudioFormat, write_wave_file


class AudioPlayer:
    def __init__(
        self,
        sampling_rate_hz: int | None = None,
        encoding: Any = None,
    ) -> None:
        if encoding is None:
            encoding = techmo_tts_pb2.AudioEncoding.PCM16  # type: ignore[attr-defined]
        self.sampling_rate_hz = sampling_rate_hz
        self.stream: sd.OutputStream | None = None

        if encoding == techmo_tts_pb2.AudioEncoding.PCM16:  # type: ignore[attr-defined]
            self.encoding = np.int16
        elif encoding == "ogg-vorbis" or encoding == "ogg-opus":
            raise RuntimeError("Audio Player supports only PCM16 audio-encoding.")
        else:
            raise RuntimeError("Unsupported audio-encoding: " + str(encoding))

    def start(self, sampling_rate_hz: int | None = None) -> None:
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

    def append(self, audio: bytes) -> None:
        if self.stream is not None:
            self.stream.write(np.frombuffer(audio, dtype=np.int16))

    def stop(self) -> None:
        if self.stream is not None:
            self.stream.close()


class AudioSaver:
    """Wave Saver for TTS"""

    _buffer: bytearray
    _framerate: int | None
    _nchannels: int
    _sampwidth: int
    _encoding: Any

    def __init__(self, sampling_frequency: int | None = None) -> None:
        self._buffer = bytearray()
        self._framerate = sampling_frequency
        self._nchannels = 1
        self._sampwidth = 2
        self._encoding = None

    def setEncoding(self, encoding: Any) -> None:
        self._encoding = encoding

    def setFrameRate(self, sampling_frequency: int) -> None:
        self._framerate = sampling_frequency

    def setSampWidth(self, sample_width: int) -> None:
        self._sampwidth = sample_width

    def append(self, audiodata: bytes) -> None:
        self._buffer += audiodata

    def clear(self) -> None:
        self._buffer.clear()

    def save(self, filename: str) -> None:
        if (
            (self._encoding == techmo_tts_pb2.AudioEncoding.PCM16)  # type: ignore[attr-defined]
            or (self._encoding == techmo_tts_pb2.AudioEncoding.A_LAW)  # type: ignore[attr-defined]
            or (self._encoding == techmo_tts_pb2.AudioEncoding.MU_LAW)  # type: ignore[attr-defined]
        ):
            if not self._framerate:
                raise RuntimeError("Sample rate has not been set")

            if self._encoding == techmo_tts_pb2.AudioEncoding.MU_LAW:  # type: ignore[attr-defined]
                audio_format = int(AudioFormat.MU_LAW)
            elif self._encoding == techmo_tts_pb2.AudioEncoding.A_LAW:  # type: ignore[attr-defined]
                audio_format = int(AudioFormat.A_LAW)
            else:
                audio_format = int(AudioFormat.PCM16)

            write_wave_file(
                filename,
                self._buffer,
                self._framerate,
                self._nchannels,
                int(self._sampwidth),
                audio_format,
            )
        else:
            with open(filename, "wb") as f:
                f.write(self._buffer)

    def load(self, filename: str) -> None:
        with wave.open(filename, "r") as wr:
            self._buffer = bytearray(wr.readframes(wr.getnframes()))

    def isEqualTo(self, asv: AudioSaver) -> bool:
        return self._buffer == asv._buffer


class GrpcRequestConfig:
    _channel: grpc.Channel | None
    _stub: Any
    _timeout: float | None
    _metadata: list[tuple[str, str]]

    def __init__(
        self,
        service_address: str,
        tls: bool,
        tls_dir: str,
        tls_ca_cert_file: str,
        tls_cert_file: str,
        tls_private_key_file: str,
        session_id: str,
        grpc_timeout: int = 0,
    ) -> None:
        self._channel = create_channel(
            service_address=service_address,
            tls=tls,
            tls_dir=tls_dir,
            tls_ca_cert_file=tls_ca_cert_file,
            tls_cert_file=tls_cert_file,
            tls_private_key_file=tls_private_key_file,
        )
        self._stub = techmo_tts_pb2_grpc.TTSStub(self._channel)  # type: ignore[no-untyped-call]
        if grpc_timeout > 0:
            self._timeout = grpc_timeout / 1000
        else:
            self._timeout = None
        self._metadata = []
        if session_id:
            self._metadata = [("session_id", session_id)]

    def get_channel(self) -> grpc.Channel | None:
        return self._channel

    def get_stub(self) -> Any:
        return self._stub

    def get_timeout(self) -> float | None:
        return self._timeout

    def get_metadata(self) -> list[tuple[str, str]]:
        return self._metadata


def print_service_version(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
) -> None:
    rc = GrpcRequestConfig(
        service_address=service_address,
        tls=tls,
        tls_dir=tls_dir,
        tls_ca_cert_file=tls_ca_cert_file,
        tls_cert_file=tls_cert_file,
        tls_private_key_file=tls_private_key_file,
        session_id=session_id,
        grpc_timeout=grpc_timeout,
    )
    request = techmo_tts_pb2.GetServiceVersionRequest()  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        response = stub.GetServiceVersion(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print(response)
    except grpc.RpcError as e:
        print_server_side_error(str(e))


def print_resources_id(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
) -> None:
    rc = GrpcRequestConfig(
        service_address=service_address,
        tls=tls,
        tls_dir=tls_dir,
        tls_ca_cert_file=tls_ca_cert_file,
        tls_cert_file=tls_cert_file,
        tls_private_key_file=tls_private_key_file,
        session_id=session_id,
        grpc_timeout=grpc_timeout,
    )
    request = techmo_tts_pb2.GetResourcesIdRequest()  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        response = stub.GetResourcesId(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print(response)
    except grpc.RpcError as e:
        print_server_side_error(str(e))


def list_voices(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
) -> None:
    rc = GrpcRequestConfig(
        service_address=service_address,
        tls=tls,
        tls_dir=tls_dir,
        tls_ca_cert_file=tls_ca_cert_file,
        tls_cert_file=tls_cert_file,
        tls_private_key_file=tls_private_key_file,
        session_id=session_id,
        grpc_timeout=grpc_timeout,
    )
    request = techmo_tts_pb2.ListVoicesRequest(language_code=language_code)  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        response = stub.ListVoices(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nAvailable voices:\n")
        print(response)
    except grpc.RpcError as e:
        print_server_side_error(str(e))


def prepare_synthesis_config(
    language_code: str,
    voice_name: str,
    voice_age: str,
    voice_gender: str,
    voice_variant: int,
    speech_pitch: float,
    speech_range: float,
    speech_rate: float,
    speech_stress: float,
    speech_volume: float,
) -> Any:
    synthesis_config = None
    voice = None
    prosodic_properties = None

    if (voice_name != "") or (voice_age != "") or (voice_gender != "") or (voice_variant != 1):
        voice = create_voice(
            voice_name=voice_name,
            voice_gender=voice_gender,
            voice_age=voice_age,
            voice_variant=voice_variant,
        )

    if (speech_pitch != 1.0) or (speech_range != 1.0) or (speech_rate != 1.0) or (speech_stress != 1.0) or (speech_volume != 1.0):
        prosodic_properties = techmo_tts_pb2.ProsodicProperties(  # type: ignore[attr-defined]
            pitch=speech_pitch,
            range=speech_range,
            rate=speech_rate,
            stress=speech_stress,
            volume=speech_volume,
        )

    if (language_code != "") or (voice is not None) or (prosodic_properties is not None):
        synthesis_config = techmo_tts_pb2.SynthesisConfig(  # type: ignore[attr-defined]
            language_code=language_code,
            voice=voice,
            prosodic_properties=prosodic_properties,
        )
        if language_code == "":
            synthesis_config.ClearField("language_code")
        if voice is None:
            synthesis_config.ClearField("voice")
        if prosodic_properties is None:
            synthesis_config.ClearField("prosodic_properties")

    return synthesis_config


def synthesize(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    audio_encoding: str,
    sampling_rate: int,
    max_frame_size: int,
    language_code: str,
    voice_name: str,
    voice_age: str,
    voice_gender: str,
    voice_variant: int,
    speech_pitch: float,
    speech_range: float,
    speech_rate: float,
    speech_stress: float,
    speech_volume: float,
    play: bool,
    response: str,
    out_path: str,
    text: str,
) -> None:
    audio_encoding = get_audio_encoding(audio_encoding=audio_encoding)
    out_path = create_out_path(out_path=out_path, audio_encoding=audio_encoding)

    channel = create_channel(
        service_address=service_address,
        tls=tls,
        tls_dir=tls_dir,
        tls_ca_cert_file=tls_ca_cert_file,
        tls_cert_file=tls_cert_file,
        tls_private_key_file=tls_private_key_file,
    )
    stub = techmo_tts_pb2_grpc.TTSStub(channel)  # type: ignore[no-untyped-call]

    synthesis_config = prepare_synthesis_config(
        language_code=language_code,
        voice_name=voice_name,
        voice_age=voice_age,
        voice_gender=voice_gender,
        voice_variant=voice_variant,
        speech_pitch=speech_pitch,
        speech_range=speech_range,
        speech_rate=speech_rate,
        speech_stress=speech_stress,
        speech_volume=speech_volume,
    )

    output_config = None

    if (audio_encoding != techmo_tts_pb2.AudioEncoding.PCM16) or (sampling_rate != 0) or (max_frame_size != 0):  # type: ignore[attr-defined]
        output_config = techmo_tts_pb2.OutputConfig(  # type: ignore[attr-defined]
            audio_encoding=audio_encoding,
            sampling_rate_hz=sampling_rate,
            max_frame_size=max_frame_size,
        )

    request = techmo_tts_pb2.SynthesizeRequest(text=text, synthesis_config=synthesis_config, output_config=output_config)  # type: ignore[attr-defined]

    if synthesis_config is None:
        request.ClearField("synthesis_config")
    if output_config is None:
        request.ClearField("output_config")

    timeout: float | None = None
    if grpc_timeout > 0:
        timeout = grpc_timeout / 1000  # milliseconds to seconds
    metadata: list[tuple[str, str]] = []
    if session_id:
        metadata = [("session_id", session_id)]

    audioPlayer: AudioPlayer | None = None
    if play:
        player_sampling_rate: int = sampling_rate if sampling_rate else 8000
        audioPlayer = AudioPlayer(sampling_rate_hz=player_sampling_rate, encoding=audio_encoding)
    audioSaver = AudioSaver()
    audioSaver.setEncoding(audio_encoding)

    if (audio_encoding == techmo_tts_pb2.AudioEncoding.A_LAW) or (audio_encoding == techmo_tts_pb2.AudioEncoding.MU_LAW):  # type: ignore[attr-defined]
        audioSaver.setSampWidth(1)

    try:
        if response == "streaming":
            internal_synthesize_streaming(stub, request, timeout, metadata, audioSaver, audioPlayer)
        elif response == "single":
            internal_synthesize(stub, request, timeout, metadata, audioSaver, audioPlayer)
        else:
            raise RuntimeError("Unsupported response type: " + response)
        audioSaver.save(out_path)
    except grpc.RpcError as e:
        print_server_side_error(str(e))
    finally:
        if audioPlayer is not None:
            audioPlayer.stop()

    audioSaver.clear()


def _read_file(path: str) -> bytes | None:
    p = Path(path)
    return p.read_bytes() if p.exists() else None


def create_channel(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
) -> grpc.Channel:
    ca_cert_file: bytes | None = None
    cert_file: bytes | None = None
    private_key_file: bytes | None = None

    if tls_dir:
        ca_cert_file = _read_file(tls_dir + "/ca.crt")
        private_key_file = _read_file(tls_dir + "/client.key")
        cert_file = _read_file(tls_dir + "/client.crt")

    if tls_ca_cert_file:
        ca_cert_file = _read_file(tls_ca_cert_file)

    if tls_private_key_file:
        private_key_file = _read_file(tls_private_key_file)

    if tls_cert_file:
        cert_file = _read_file(tls_cert_file)

    if (ca_cert_file is None) and (cert_file is None) and (private_key_file is None) and (not tls):
        return grpc.insecure_channel(service_address)
    else:
        return grpc.secure_channel(
            service_address,
            grpc.ssl_channel_credentials(ca_cert_file, private_key_file, cert_file),
        )


def create_out_path(
    out_path: str,
    audio_encoding: Any,
) -> str:
    if out_path == "":
        if (
            (audio_encoding == techmo_tts_pb2.AudioEncoding.PCM16)  # type: ignore[attr-defined]
            or (audio_encoding == techmo_tts_pb2.AudioEncoding.A_LAW)  # type: ignore[attr-defined]
            or (audio_encoding == techmo_tts_pb2.AudioEncoding.MU_LAW)  # type: ignore[attr-defined]
        ):
            out_path = "output.wav"
        elif (audio_encoding == techmo_tts_pb2.AudioEncoding.OGG_VORBIS) or (audio_encoding == techmo_tts_pb2.AudioEncoding.OGG_OPUS):  # type: ignore[attr-defined]
            out_path = "output.ogg"
        else:
            raise RuntimeError("Unsupported audio encoding: " + str(audio_encoding))
    return out_path


def create_voice(
    voice_name: str,
    voice_gender: str,
    voice_age: str,
    voice_variant: int,
) -> Any:
    try:
        gender = None
        age = None
        if voice_gender == "female":
            gender = techmo_tts_pb2.Gender.FEMALE  # type: ignore[attr-defined]
        elif voice_gender == "male":
            gender = techmo_tts_pb2.Gender.MALE  # type: ignore[attr-defined]
        elif voice_gender != "":
            raise RuntimeError("Unsupported voice-gender: " + voice_gender)

        if voice_age == "adult":
            age = techmo_tts_pb2.Age.ADULT  # type: ignore[attr-defined]
        elif voice_age == "child":
            age = techmo_tts_pb2.Age.CHILD  # type: ignore[attr-defined]
        elif voice_age == "senile":
            age = techmo_tts_pb2.Age.SENILE  # type: ignore[attr-defined]
        elif voice_age != "":
            raise RuntimeError("Unsupported voice-age: " + voice_age)

        return techmo_tts_pb2.Voice(name=voice_name, gender=gender, age=age, variant=voice_variant)  # type: ignore[attr-defined]
    except RuntimeError:
        raise
    except Exception as err:
        raise RuntimeError("Unable to create voice!") from err


def get_audio_encoding(audio_encoding: str) -> Any:
    if audio_encoding == "pcm16":
        return techmo_tts_pb2.AudioEncoding.PCM16  # type: ignore[attr-defined]
    elif audio_encoding == "ogg-vorbis":
        return techmo_tts_pb2.AudioEncoding.OGG_VORBIS  # type: ignore[attr-defined]
    elif audio_encoding == "ogg-opus":
        return techmo_tts_pb2.AudioEncoding.OGG_OPUS  # type: ignore[attr-defined]
    elif audio_encoding == "a-law":
        return techmo_tts_pb2.AudioEncoding.A_LAW  # type: ignore[attr-defined]
    elif audio_encoding == "mu-law":
        return techmo_tts_pb2.AudioEncoding.MU_LAW  # type: ignore[attr-defined]
    else:
        raise RuntimeError("Unsupported audio-encoding: " + audio_encoding)


def internal_synthesize(
    stub: Any,
    request: Any,
    timeout: float | None,
    metadata: list[tuple[str, str]],
    audio_saver: AudioSaver,
    audio_player: AudioPlayer | None,
) -> None:
    response = stub.Synthesize(request, timeout=timeout, metadata=metadata)
    print_warnings(response.warnings)
    if audio_player is not None:
        audio_player.start(sampling_rate_hz=response.sampling_rate_hz)
        audio_player.append(response.audio)
    audio_saver.setFrameRate(response.sampling_rate_hz)
    audio_saver.append(response.audio)


def internal_synthesize_streaming(
    stub: Any,
    request: Any,
    timeout: float | None,
    metadata: list[tuple[str, str]],
    audio_saver: AudioSaver,
    audio_player: AudioPlayer | None,
) -> None:
    if audio_player is not None:
        audio_player.start()
    for response in stub.SynthesizeStreaming(request, timeout=timeout, metadata=metadata):
        print_warnings(response.warnings)
        if audio_saver._framerate:
            if audio_saver._framerate != response.sampling_rate_hz:
                raise RuntimeError("Sample rate does not match previously received.")
        else:
            audio_saver.setFrameRate(response.sampling_rate_hz)
        if audio_player is not None:
            audio_player.append(response.audio)
        audio_saver.append(response.audio)


def print_warnings(warnings: Any) -> None:
    if warnings:
        print("The following warnings were encountered:")
        for w in warnings:
            print(w)


def print_server_side_error(e: str) -> None:
    if "UNAVAILABLE" in e:
        print("Unable to connect to the service! Check if the service-address and TLS settings are correct.")
    elif "UNIMPLEMENTED" in e:
        print("[Server-side error] Feature not implemented! \n Presumably the service being queried supports a different version of the API.")
    else:
        print(
            "[Server-side error] Received following RPC error from the TTS service: ",
            e,
        )
