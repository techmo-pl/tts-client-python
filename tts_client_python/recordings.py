from tts_client_python.proto import techmo_tts_pb2 as techmo_tts_pb2
from tts_client_python.proto import techmo_tts_pb2_grpc as techmo_tts_pb2_grpc
import grpc
import os
import wave
from tts_client_python.general import GrpcRequestConfig


def delete_recording(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.DeleteRecordingRequest(
        voice_name=args.delete_recording[0], recording_key=args.delete_recording[1]
    )

    try:
        stub = rc.get_stub()
        response = stub.DeleteRecording(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        print("\nRecording: ", args.delete_recording[1], " has been deleted\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def get_recording(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )

    output_path = ""
    if args.get_recording[2] != "":
        output_path = args.get_recording[2]
    else:
        output_path = args.get_recording[1] + ".wav"

    request = techmo_tts_pb2.GetRecordingRequest(
        voice_name=args.get_recording[0], recording_key=args.get_recording[1]
    )

    try:
        stub = rc.get_stub()
        response = stub.GetRecording(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )

    wave_write = wave.open(output_path, "wb")
    wave_write.setnchannels(1)
    wave_write.setsampwidth(2)
    wave_write.setframerate(response.sampling_rate_hz)
    wave_write.writeframes(response.content)
    wave_write.close()


def list_recordings(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    voice_name = args.voice_to_list_recordings_for
    request = techmo_tts_pb2.ListRecordingsRequest(voice_name=voice_name)

    try:
        stub = rc.get_stub()
        response = stub.ListRecordings(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        print('\nAvailable recording keys for the voice "' + voice_name + '":\n')
        print(*response.keys, sep="\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def put_recording(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )

    audio_path = args.put_recording[2]
    wave_read = wave.open(audio_path, "rb")
    channels = wave_read.getnchannels()
    sample_width = wave_read.getsampwidth()
    sampling_rate = wave_read.getframerate()

    if channels != 1:
        raise ValueError(
            "Only mono waves are allowed. {} contains: {} channels".format(
                audio_path, channels
            )
        )

    if sample_width != 2:
        raise ValueError(
            "Only 16bit samples are allowed. {} has: {} bit samples".format(
                audio_path, sample_width * 8
            )
        )

    audio_content_array = bytearray()
    for i in range(wave_read.getnframes()):
        audio_content_array.extend(wave_read.readframes(i))

    wave_read.close()
    audio_content = bytes(audio_content_array)

    request = techmo_tts_pb2.PutRecordingRequest(
        voice_name=args.put_recording[0],
        recording_key=args.put_recording[1],
        sampling_rate_hz=sampling_rate,
        content=audio_content,
    )

    try:
        stub = rc.get_stub()
        stub.PutRecording(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nRecording: ", args.put_recording[1], " has been added\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )
