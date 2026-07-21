"""Update device attributes for the floor heater thermostat in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

FLOORHEATER_TYPE = "Floorheater"
FLOORHEATER_MODEL = "Schluter Thermostat"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "expected_json",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the netscanner JSON file (reads from stdin if omitted)",
    )
    args = parser.parse_args()

    if args.expected_json is None:
        data = json.load(sys.stdin)
    else:
        data = json.loads(args.expected_json.read_text())

    for device in data["devices"]:
        if device.get("hostname") != "floorheatt-stat":
            continue
        device["type"] = FLOORHEATER_TYPE
        device["model"] = FLOORHEATER_MODEL
        print(f"Updated {device['mac']} -> type = '{FLOORHEATER_TYPE}', model = '{FLOORHEATER_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
