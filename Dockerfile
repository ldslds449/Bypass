FROM ubuntu:24.04

ENV PORT=5050
ENV BYPASS_IP=127.0.0.1
ENV BYPASS_PORT=8282

WORKDIR /app
USER root

RUN apt update && apt install -y git python3-pip python3.12-venv
RUN python3 -m venv env
ENV PATH="/app/env/bin:$PATH"

RUN git clone https://github.com/ldslds449/Bypass
WORKDIR /app/Bypass
RUN pip install -r requirements.txt

EXPOSE $PORT
CMD python3 /app/Bypass/bypass.py --hostname 0.0.0.0 --port $PORT --bypass-ip $BYPASS_IP --bypass-port $BYPASS_PORT
