FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive


RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
    gnupg2 ca-certificates libpq-dev git build-essential x264 libx264-dev libopencv-dev python3 python3-pip ffmpeg \
    python3-opencv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /usr/src/project



# RUN pip3 install --upgrade pip && pip3 install -r ./general_requirements.txt

ENTRYPOINT python3 main.py
