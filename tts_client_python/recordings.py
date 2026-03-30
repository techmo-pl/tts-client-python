from __future__ import annotations

import wave

import grpc

from tts_client_python.general import GrpcRequestConfig
from techmo.tts.api.v3 import techmo_tts_pb2
from tts_client_python.wave_utils import AudioFormat, write_wave_file


def delete_recording(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
    voice_name: str,
    voice_variant: int,
    recording_key: str,
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
    request = techmo_tts_pb2.DeleteRecordingRequest(  # type: ignore[attr-defined]
        voice_profile=techmo_tts_pb2.VoiceProfile(  # type: ignore[attr-defined]
            voice_name=voice_name,
            voice_variant=voice_variant,
            language_code=language_code,
        ),
        recording_key=recording_key,
    )

    try:
        stub = rc.get_stub()
        stub.DeleteRecording(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nRecording: ", recording_key, " has been deleted\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def get_recording(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
    voice_name: str,
    voice_variant: int,
    recording_key: str,
    output_path: str,
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

    out_path = output_path if output_path != "" else recording_key + ".wav"

    request = techmo_tts_pb2.GetRecordingRequest(  # type: ignore[attr-defined]
        voice_profile=techmo_tts_pb2.VoiceProfile(  # type: ignore[attr-defined]
            voice_name=voice_name,
            voice_variant=voice_variant,
            language_code=language_code,
        ),
        recording_key=recording_key,
    )
    try:
        stub = rc.get_stub()
        response = stub.GetRecording(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )
        return

    write_wave_file(
        out_path,
        response.content,
        response.sampling_rate_hz,
        1,
        2,
        int(AudioFormat.PCM16),
    )


def list_recordings(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
    voice_name: str,
    voice_variant: int,
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
    request = techmo_tts_pb2.ListRecordingsRequest(  # type: ignore[attr-defined]
        voice_profile=techmo_tts_pb2.VoiceProfile(  # type: ignore[attr-defined]
            voice_name=voice_name,
            voice_variant=voice_variant,
            language_code=language_code,
        ),
    )

    try:
        stub = rc.get_stub()
        response = stub.ListRecordings(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print('\nAvailable recording keys for the voice "' + voice_name + '":\n')
        print(*response.keys, sep="\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def list_sound_icons(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
    voice_name: str,
    voice_variant: int,
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
    request = techmo_tts_pb2.ListSoundIconsRequest(  # type: ignore[attr-defined]
        voice_profile=techmo_tts_pb2.VoiceProfile(  # type: ignore[attr-defined]
            voice_name=voice_name,
            voice_variant=voice_variant,
            language_code=language_code,
        ),
    )

    try:
        stub = rc.get_stub()
        response = stub.ListSoundIcons(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print('\nAvailable sound icons keys for the voice "' + voice_name + '":\n')
        print(*response.keys, sep="\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def put_recording(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    language_code: str,
    voice_name: str,
    voice_variant: int,
    recording_key: str,
    audio_path: str,
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

    with wave.open(audio_path, "rb") as wave_read:
        channels = wave_read.getnchannels()
        sample_width = wave_read.getsampwidth()
        sampling_rate = wave_read.getframerate()

        if channels != 1:
            raise ValueError(f"Only mono waves are allowed. {audio_path} contains: {channels} channels")

        if sample_width != 2:
            raise ValueError(f"Only 16bit samples are allowed. {audio_path} has: {sample_width * 8} bit samples")

        audio_content = bytes(wave_read.readframes(wave_read.getnframes()))

    request = techmo_tts_pb2.PutRecordingRequest(  # type: ignore[attr-defined]
        voice_profile=techmo_tts_pb2.VoiceProfile(  # type: ignore[attr-defined]
            voice_name=voice_name,
            voice_variant=voice_variant,
            language_code=language_code,
        ),
        recording_key=recording_key,
        sampling_rate_hz=sampling_rate,
        content=audio_content,
    )

    try:
        stub = rc.get_stub()
        stub.PutRecording(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nRecording: ", recording_key, " has been added\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )
