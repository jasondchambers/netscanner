#!/usr/bin/env bash

uv run netscanner --host 10.27.27.1 >expected.json

cat expected.json |
  uv run update-ring-devices data/ring_devices.txt |
  uv run update-sonos-devices data/sonos_system.txt |
  uv run update-eero-devices |
  uv run initialize-type-model-attributes \
    >enriched.json
