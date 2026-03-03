FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends mosquitto \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paho-mqtt

WORKDIR /app

COPY mosquitto.conf /etc/mosquitto/mosquitto.conf
COPY simulator.py   .
COPY entrypoint.sh  .
RUN chmod +x entrypoint.sh

EXPOSE 1883

ENTRYPOINT ["./entrypoint.sh"]
