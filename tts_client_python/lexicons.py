from tts_client_python.proto import techmo_tts_pb2 as techmo_tts_pb2
from tts_client_python.proto import techmo_tts_pb2_grpc as techmo_tts_pb2_grpc
import grpc
import os
from tts_client_python.general import GrpcRequestConfig
import lxml.etree as etree


def delete_lexicon(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.DeleteLexiconRequest(name=args.lexicon_to_delete)

    try:
        stub = rc.get_stub()
        response = stub.DeleteLexicon(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        print("\nLexicon: ", args.lexicon_to_delete, " has been deleted\n")
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def get_lexicon(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.GetLexiconRequest(name=args.lexicon_to_get)

    try:
        stub = rc.get_stub()
        response = stub.GetLexicon(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        xml_parser = etree.XMLParser(remove_blank_text=True, recover=True)
        x = etree.fromstring(response.content, parser=xml_parser)
        print("\n---", args.lexicon_to_get, "---\n")
        print(etree.tostring(x, pretty_print=True).decode())
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def list_lexicons(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.ListLexiconsRequest(language=args.language)

    try:
        stub = rc.get_stub()
        response = stub.ListLexicons(
            request, timeout=rc.get_timeout(), metadata=rc.get_metadata()
        )
        print("\nAvailable lexicons:\n")
        print(response)
    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )


def put_lexicon(args):

    rc = GrpcRequestConfig(
        service=args.service,
        tls_directory=args.tls_directory,
        grpc_timeout=args.grpc_timeout,
        session_id=args.session_id,
    )
    request = techmo_tts_pb2.PutLexiconRequest(
        name=args.put_lexicon[0], content=args.put_lexicon[1]
    )

    try:
        stub = rc.get_stub()
        stub.PutLexicon(request, timeout=rc.get_timeout(), metadata=rc.get_metadata())
        print("\nLexicon: ", args.put_lexicon[0], " has been added\n")

    except grpc.RpcError as e:
        print(
            "[Server-side error] Received following RPC error from the TTS service:",
            str(e),
        )
