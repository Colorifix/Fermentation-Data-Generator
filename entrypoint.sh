#!/bin/sh
set -e

# Start the Mosquitto broker in the background
mosquitto -c /etc/mosquitto/mosquitto.conf &

# Wait for the broker to be ready
sleep 1

# Run the simulator, forwarding all arguments
exec python simulator.py "$@"
