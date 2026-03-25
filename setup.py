from __future__ import annotations

from pathlib import Path
from typing import Any

from setuptools import Command, find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install

# Read version without importing the package — avoids a circular import during
# the PEP-517 build phase (setup.py is executed before the package is installed).
_version_ns: dict[str, object] = {}
exec(  # noqa: S102
    (Path(__file__).parent / "tts_client_python" / "VERSION.py").read_text(),
    _version_ns,
)
package_version: str = str(_version_ns["TTS_CLIENT_PYTHON_VERSION"])

project_root = Path(__file__).parent


class BuildPackageProtos(Command):  # type: ignore[misc]
    """Command to generate project *_pb2.py modules from proto files."""

    user_options: list[Any] = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        """Build gRPC modules."""
        import shutil

        import grpc_tools
        from grpc_tools import protoc

        temp_proto_dir = project_root / "tts_service_api"
        try:
            proto_file = project_root / "submodules" / "tts-service-api" / "proto" / "techmo_tts.proto"
            output_path = project_root / "tts_client_python" / "proto"
            if not proto_file.exists():
                raise FileNotFoundError(
                    f"Proto source file not found: {proto_file}\n"
                    "The 'tts-service-api' submodule is not initialised.\n"
                    "Run ./setup.sh first, then re-run ./install.sh."
                )
            if grpc_tools.__file__ is None:
                raise RuntimeError("Cannot locate grpc_tools package directory")
            well_known_protos_include = str(Path(grpc_tools.__file__).parent / "_proto")
            shutil.rmtree(temp_proto_dir, ignore_errors=True)
            temp_proto_dir.mkdir()
            shutil.copy(proto_file, temp_proto_dir)

            command_1 = [
                "grpc_tools.protoc",
                f"--proto_path={output_path.relative_to(project_root)}={temp_proto_dir.name}",
                f"--proto_path={well_known_protos_include}",
                f"--python_out={project_root.relative_to(project_root)}",
                f"--grpc_python_out={project_root.relative_to(project_root)}",
            ] + [str(temp_proto_dir.relative_to(project_root) / proto_file.name)]

            if protoc.main(command_1) != 0:
                raise Exception("Problem with building gRPC modules")
        except Exception as e:
            print(e)
            raise
        finally:
            shutil.rmtree(temp_proto_dir, ignore_errors=True)


class BuildPyGRPC(build_py):  # type: ignore[misc]
    """Command for Python modules build."""

    def __init__(self, dist: Any) -> None:
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self) -> None:
        """Build Python and GRPC modules."""
        super().run()
        self.subcommand.run()


class DevelopGRPC(develop):  # type: ignore[misc]
    """Command for develop installation."""

    def __init__(self, dist: Any) -> None:
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self) -> None:
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()


class CustomInstall(install):  # type: ignore[misc]
    """Command for pip installation."""

    def __init__(self, dist: Any) -> None:
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self) -> None:
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()


class CustomEggInfo(egg_info):  # type: ignore[misc]
    """Command for pip installation."""

    def __init__(self, dist: Any) -> None:
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self) -> None:
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()


setup(
    name="tts_client_python",
    version=package_version,
    author="Jan Woźniak",
    description="Techmo TTS DNN grpc python client",
    long_description=(project_root / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/techmo-pl/tts-client-python",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Generated stubs embed GRPC_GENERATED_VERSION='1.70.0' and raise
        # RuntimeError for grpcio<1.70.0.  grpcio 1.71.0 dropped Python 3.8.
        # Python 3.9+ uses a recent known-good version (1.70.0) as lower bound.
        "grpcio>=1.70.0,<2.0.0; python_version>='3.9'",
        "grpcio>=1.70.0,<1.71.0; python_version=='3.8'",
        # Stubs are generated with protobuf 5.29.x; runtime must be >=5.29.0.
        # protobuf 6.x requires Python>=3.9, so cap at <6.0 for Python 3.8.
        "protobuf>=5.29.0,<6.0.0; python_version=='3.8'",
        "protobuf>=5.29.0; python_version>='3.9'",
        "lxml>=4.6.4",
        "numpy>=1.19.5",
        "sounddevice>=0.4.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "jiwer>=3.0",
        ],
    },
    python_requires=">=3.8",
    project_urls={
        "Source": "https://github.com/techmo-pl/tts-client-python",
        "Documentation": "https://github.com/techmo-pl/tts-service-api/blob/master/doc/Documentation.md",
    },
    entry_points={"console_scripts": ["tts_client = tts_client_python.tts_client:main"]},
    cmdclass={
        "build_py": BuildPyGRPC,
        "build_grpc": BuildPackageProtos,
        "develop": DevelopGRPC,
        "egg_info": CustomEggInfo,
        "install": CustomInstall,
    },
)
