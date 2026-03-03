#!/usr/bin/env python3
"""Fermentation data simulator — publishes MQTT messages for 3 fermentors every 3 seconds."""

import json
import random
import signal
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
FERMENTOR_IDS = ["fermentor-1", "fermentor-2", "fermentor-3"]
INTERVAL = 3


class FermentorSimulator:
    def __init__(self, fermentor_id: str):
        self.fermentor_id = fermentor_id
        self.temperature = 37.0 + random.uniform(-1.0, 1.0)
        self._temp_drift = random.uniform(-0.05, 0.05)
        self.ph = 6.8 + random.uniform(-0.2, 0.2)
        self._ph_drift = random.uniform(-0.005, 0.005)

    def _next_value(self, current, drift, center, max_offset, noise_scale):
        pull = (center - current) * 0.05
        new_drift = drift + pull + random.uniform(-noise_scale * 0.5, noise_scale * 0.5)
        new_drift = max(-max_offset * 0.1, min(max_offset * 0.1, new_drift))
        new_value = current + new_drift + random.uniform(-noise_scale, noise_scale)
        new_value = max(center - max_offset, min(center + max_offset, new_value))
        return new_value, new_drift

    def step(self):
        self.temperature, self._temp_drift = self._next_value(
            self.temperature, self._temp_drift, center=37.0, max_offset=2.0, noise_scale=0.05,
        )
        self.ph, self._ph_drift = self._next_value(
            self.ph, self._ph_drift, center=6.8, max_offset=0.5, noise_scale=0.005,
        )
        return {"temperature": round(self.temperature, 2), "ph": round(self.ph, 3)}


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
simulators = {fid: FermentorSimulator(fid) for fid in FERMENTOR_IDS}


def on_connect(_client, _userdata, _flags, reason_code, _properties):
    if reason_code == 0:
        print(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"Failed to connect, reason code: {reason_code}", file=sys.stderr)
        sys.exit(1)


def shutdown(sig, frame):
    print("\nShutting down...")
    client.loop_stop()
    client.disconnect()
    sys.exit(0)


client.on_connect = on_connect
client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
client.loop_start()

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print(f"Simulating {len(FERMENTOR_IDS)} fermentors, publishing every {INTERVAL}s. Press Ctrl+C to stop.\n")

while True:
    for fid, sim in simulators.items():
        for metric, value in sim.step().items():
            topic = f"fermentors/{fid}/{metric}"
            payload = json.dumps({
                "fermentor_id": fid,
                "metric": metric,
                "value": value,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
            client.publish(topic, payload, qos=1)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {topic} → {payload}")

    time.sleep(INTERVAL)
