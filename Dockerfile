FROM python:3.6-slim

LABEL maintainer="<jan.wozniak@techmo.pl>"
ARG DEBIAN_FRONTEND=noninteractive

ADD ./tts_client_python /tts_client/tts_client_python
ADD ./requirements.txt setup.py README.md /tts_client/

WORKDIR /tts_client

RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libportaudio2 \
        python3-pip \
        python3-dev \
    && apt-get clean \
	&& rm -fr /var/lib/apt/lists/* \
	&& rm -fr /var/cache/apt/* \
    && pip3 install -r requirements.txt \
    && pip install -e .

ENTRYPOINT ["python3", "tts_client_python/tts_client.py"]
