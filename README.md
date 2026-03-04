# Fermentation Data Generator

Simulates sensor readings (temperature and pH) from 3 fermentors and publishes them as MQTT messages every 3 seconds. The container runs a Mosquitto broker and the simulator together.

## Build

```bash
docker build -t fermentation-simulator .
```

## Run

```bash
docker run -d --name fermentation-sim -p 1883:1883 fermentation-simulator
```

## Stop

```bash
docker rm -f fermentation-sim
```

## Connecting to the broker

The container exposes the Mosquitto MQTT broker on **port 1883** (no authentication required).

| Setting  | Value       |
|----------|-------------|
| Host     | `localhost`  |
| Port     | `1883`       |
| Protocol | MQTT v3.1.1 |

Subscribe to all fermentor topics with any MQTT client, for example using `mosquitto_sub`:

```bash
mosquitto_sub -h localhost -p 1883 -t "fermentors/#" -v
```

Or subscribe to a specific metric:

```bash
mosquitto_sub -h localhost -p 1883 -t "fermentors/fermentor-1/temperature" -v
```

## MQTT topics

```
fermentors/{fermentor_id}/temperature
fermentors/{fermentor_id}/ph
```

**Payload:**
```json
{
  "fermentor_id": "fermentor-1",
  "metric": "temperature",
  "value": 36.87,
  "timestamp": "2026-03-03T10:00:02Z"
}
```
