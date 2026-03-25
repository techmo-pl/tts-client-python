from __future__ import annotations

from pathlib import Path

import grpc
from grpc import StatusCode

from tts_client_python.general import GrpcRequestConfig
from tts_client_python.proto import techmo_tts_pb2 as techmo_tts_pb2


def delete_lexicon(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    lexicon_uri: str,
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
    request = techmo_tts_pb2.DeleteLexiconRequest(uri=lexicon_uri)  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        stub.DeleteLexicon(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nLexicon: ", lexicon_uri, " has been deleted\n")
    except grpc.RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            print(f"[NOT FOUND] Lexicon '{lexicon_uri}' was not found. Use --list-lexicons to find available lexicons.")
        else:
            print(
                "[Server-side error] Received following RPC error from the TTS service:",
                str(e),
            )


def get_lexicon(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    lexicon_uri: str,
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
    request = techmo_tts_pb2.GetLexiconRequest(uri=lexicon_uri)  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        response = stub.GetLexicon(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        with open(output_path, "w") as file:
            file.write(response.content)
    except grpc.RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            print(f"[NOT FOUND] Lexicon '{lexicon_uri}' was not found. Use --list-lexicons to find available lexicons.")
        else:
            print(
                "[Server-side error] Received following RPC error from the TTS service:",
                str(e),
            )


def list_lexicons(
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
    request = techmo_tts_pb2.ListLexiconsRequest(language_code=language_code)  # type: ignore[attr-defined]

    try:
        stub = rc.get_stub()
        response = stub.ListLexicons(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nAvailable lexicons:\n")
        print(response)
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def put_lexicon(
    service_address: str,
    tls: bool,
    tls_dir: str,
    tls_ca_cert_file: str,
    tls_cert_file: str,
    tls_private_key_file: str,
    session_id: str,
    grpc_timeout: int,
    lexicon_uri: str,
    lexicon_path: str,
    outside_lookup_behaviour: str,
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
    lexicon_content = Path(lexicon_path).read_text()

    outside_lookup = None
    if outside_lookup_behaviour == "allowed":
        outside_lookup = techmo_tts_pb2.OutsideLookupBehaviour.ALLOWED  # type: ignore[attr-defined]
    elif outside_lookup_behaviour == "disallowed":
        outside_lookup = techmo_tts_pb2.OutsideLookupBehaviour.DISALLOWED  # type: ignore[attr-defined]
    else:
        raise RuntimeError("Illegal value for OUTSIDE_LOOKUP_BEHAVIOUR")

    request = techmo_tts_pb2.PutLexiconRequest(  # type: ignore[attr-defined]
        uri=lexicon_uri,
        content=lexicon_content,
        outside_lookup_behaviour=outside_lookup,
    )

    try:
        stub = rc.get_stub()
        stub.PutLexicon(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nLexicon: ", lexicon_uri, " has been added\n")

    except grpc.RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            print(f"[NOT FOUND] Lexicon '{lexicon_uri}' was not found. Use --list-lexicons to find available lexicons.")
        else:
            print(
                "[Server-side error] Received following RPC error from the TTS service:",
                str(e),
            )
