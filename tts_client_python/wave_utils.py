import struct
from enum import IntEnum


class AudioFormat(IntEnum):
    PCM16 = 1
    A_LAW = 6
    MU_LAW = 7


def write_wave_file(
    filename: str,
    data: bytearray,
    samplerate: int,
    numchannels: int,
    sampwidth: int,
    audio_format: int,
) -> None:
    data_size = len(data)

    with open(filename, "wb") as f:
        # header
        f.write(
            struct.pack(
                "<4sL4s4sLHHLLHH4sL",
                b"RIFF",
                36 + data_size,
                b"WAVE",
                b"fmt ",
                16,
                audio_format,
                numchannels,
                samplerate,
                int(numchannels * samplerate * sampwidth),
                int(numchannels * sampwidth),
                sampwidth * 8,
                b"data",
                data_size,
            )
        )
        # data
        f.write(data)
