from pathlib import Path

from setuptools import Command
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import pkg_resources
from tts_client_python.VERSION import TTS_CLIENT_PYTHON_VERSION as package_version

project_root = Path(__file__).parent


class BuildPackageProtos(Command):
    """Command to generate project *_pb2.py modules from proto files."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Build gRPC modules."""
        from grpc_tools import protoc
        import shutil

        try:
            proto_file = (
                project_root
                / "submodules"
                / "tts-service-api"
                / "proto"
                / "techmo_tts.proto"
            )
            output_path = project_root / "tts_client_python" / "proto"
            well_known_protos_include = pkg_resources.resource_filename(
                "grpc_tools", "_proto"
            )
            temp_proto_dir = project_root / "tts_service_api"
            Path.mkdir(temp_proto_dir)
            shutil.copy(proto_file, temp_proto_dir)

            command = [
                "grpc_tools.protoc",
                f"--proto_path={output_path.relative_to(project_root)}={temp_proto_dir.name}",
                "--proto_path={}".format(well_known_protos_include),
                f"--python_out={project_root.relative_to(project_root)}",
                f"--grpc_python_out={project_root.relative_to(project_root)}",
            ] + [str(temp_proto_dir.relative_to(project_root) / proto_file.name)]

            if protoc.main(command) != 0:
                raise Exception("Problem with building gRPC modules")
        except Exception as e:
            print(e)
        finally:
            shutil.rmtree(temp_proto_dir, ignore_errors=True)


class BuildPyGRPC(build_py):
    """Command for Python modules build."""

    def __init__(self, dist):
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self):
        """Build Python and GRPC modules."""
        super().run()
        self.subcommand.run()


class DevelopGRPC(develop):
    """Command for develop installation."""

    def __init__(self, dist):
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self):
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()


class CustomInstall(install):
    """Command for pip installation."""

    def __init__(self, dist):
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self):
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()
        self.subcommand.run()


class CustomEggInfo(egg_info):
    """Command for pip installation."""

    def __init__(self, dist):
        """Create a sub-command to execute."""
        self.subcommand = BuildPackageProtos(dist)
        super().__init__(dist)

    def run(self):
        """Build GRPC modules before the default installation."""
        self.subcommand.run()
        super().run()


with open("README.md") as f:
    long_description = f.read()
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
        "grpcio>=1.38.1, <2.0.0",
        "protobuf>=3.15.8, <5.0.0",
        "lxml>=4.6.4, <5.0.0",
        "numpy>=1.19.5, <2.0.0",
        "sounddevice>=0.4.0, <0.5.0",
    ],
    setup_requires=[
        "grpcio-tools>=1.38.1, <2.0.0",
        "pip>=21.3.1, <23.0.0",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["tts_client = tts_client_python.tts_client:main"]
    },
    cmdclass={
        "build_py": BuildPyGRPC,
        "build_grpc": BuildPackageProtos,
        "develop": DevelopGRPC,
        "egg_info": CustomEggInfo,
        "install": CustomInstall,
    },
)
