#!/usr/bin/env bash

uv run netscanner --host 10.27.27.1 >expected.json

cat expected.json |
  uv run update-ring-devices data/ring_devices.txt |
  uv run update-sonos-devices data/sonos_system.txt |
  uv run update-eero-devices |
  uv run update-printer-devices |
  uv run update-floorheater-devices |
  uv run update-pc-devices |
  uv run update-appletv-devices |
  uv run update-pictureframe-devices |
  uv run update-garagedoor-devices |
  uv run update-arlo-devices |
  uv run update-echo-devices |
  uv run update-networking-devices |
  uv run update-smartplug-devices |
  uv run initialize-type-model-attributes \
    >enriched.json
