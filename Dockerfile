FROM python:3.8-slim AS build-stage

ARG DEBIAN_FRONTEND=noninteractive
ENV PIP_ROOT_USER_ACTION=ignore

COPY tts_client_python /tts-client-python/tts_client_python
COPY setup.py pyproject.toml README.md /tts-client-python/

WORKDIR /tts-client-python

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libportaudio2 \
        python3-pip \
        python3-dev \
    && apt-get clean \
	&& rm -fr /var/lib/apt/lists/* \
	&& rm -fr /var/cache/apt/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .


FROM python:3.8-slim

LABEL maintainer="Techmo sp. z o.o. <https://github.com/techmo-pl>"

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libportaudio2 \
    && apt-get clean \
	&& rm -fr /var/lib/apt/lists/* \
	&& rm -fr /var/cache/apt/*

COPY --from=build-stage /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=build-stage /tts-client-python/tts_client_python /tts-client-python/tts_client_python

WORKDIR /tts-client-python

COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
