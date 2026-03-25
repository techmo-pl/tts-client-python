from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import MagicMock

import pytest


def _sounddevice_probe() -> str:
    """Probe whether sounddevice can be imported in a subprocess.

    Returns:
        "ok"      — importable without issues
        "crash"   — killed by a signal (e.g. SIGSEGV from PortAudio in headless env)
        "error"   — import failed with a Python exception (missing package, broken dep)
    """
    result = subprocess.run(
        [sys.executable, "-c", "import sounddevice"],
        capture_output=True,
        timeout=10,
    )
    if result.returncode == 0:
        return "ok"
    # Negative return code on Linux means the process was killed by a signal
    # (e.g. -11 = SIGSEGV from PortAudio Pa_Initialize() in headless environments).
    if result.returncode < 0:
        return "crash"
    # Any other non-zero exit: a Python exception (ModuleNotFoundError, ImportError,
    # OSError for missing libportaudio, etc.).  Let these fail naturally so dependency
    # problems are visible.
    return "error"


# sounddevice calls Pa_Initialize() at module level, which can segfault in headless
# environments (no audio hardware).  No tests exercise real audio playback, so
# replacing it with a MagicMock is safe.
# We only mock on signal-kill (segfault); Python-level errors are left to fail
# naturally so that dependency problems remain visible.
_probe = _sounddevice_probe()
if _probe == "crash":
    sys.modules["sounddevice"] = MagicMock()
elif _probe == "error":
    import ctypes.util

    if ctypes.util.find_library("portaudio") is None:
        print(
            "\nWarning: libportaudio2 is not installed — sounddevice will fail on import.\nFix: sudo apt-get install libportaudio2\n",
            file=sys.stderr,
        )


@pytest.fixture(scope="session")
def tts_service_address() -> str:
    """Return TTS_SERVICE_ADDRESS from the environment.

    Tests using this fixture are automatically skipped when the variable is not set.
    Set TTS_VOICE_NAME and TTS_LANGUAGE_CODE to target a specific voice (optional).
    """
    addr = os.environ.get("TTS_SERVICE_ADDRESS", "")
    if not addr:
        pytest.skip("TTS_SERVICE_ADDRESS not set — skipping TTS integration tests")
    return addr
