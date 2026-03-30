from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

# Read version without importing the package — avoids a circular import during
# the PEP-517 build phase (setup.py is executed before the package is installed).
_version_ns: dict[str, object] = {}
exec(  # noqa: S102
    (Path(__file__).parent / "tts_client_python" / "VERSION.py").read_text(),
    _version_ns,
)
package_version: str = str(_version_ns["TTS_CLIENT_PYTHON_VERSION"])

project_root = Path(__file__).parent

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
        # gRPC stubs come from tts-api; grpcio is also needed directly for channel creation.
        # grpcio 1.71.0 dropped Python 3.8; keep <1.71.0 for 3.8 compatibility.
        "grpcio>=1.70.0,<2.0.0; python_version>='3.9'",
        "grpcio>=1.70.0,<1.71.0; python_version=='3.8'",
        # Pre-built gRPC stubs for the Techmo TTS API.
        # Switch to "tts-api>=3.2.1" once published to PyPI.
        "tts-api @ git+https://github.com/techmo-pl/tts-api-python.git",
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
        "Documentation": "https://github.com/techmo-pl/tts-api/blob/master/doc/Documentation.md",
    },
    entry_points={"console_scripts": ["tts_client = tts_client_python.tts_client:main"]},
)
