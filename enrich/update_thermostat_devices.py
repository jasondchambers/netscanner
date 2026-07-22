"""Update device attributes for Honeywell/Resideo thermostat gateways in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

THERMOSTAT_TYPE = "Thermostat"
THERMOSTAT_MODEL = "Honeywell/Resideo"

THERMOSTAT_HOSTNAMES = {"gateway8b7c2f", "gatewaya4b553"}


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
        if device.get("hostname") not in THERMOSTAT_HOSTNAMES:
            continue
        device["type"] = THERMOSTAT_TYPE
        device["model"] = THERMOSTAT_MODEL
        print(f"Updated {device['mac']} -> type = '{THERMOSTAT_TYPE}', model = '{THERMOSTAT_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
