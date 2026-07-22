"""Update device attributes for TP-Link smart plugs in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

SMARTPLUG_TYPE = "Smart Plug"

SMARTPLUG_MODELS_BY_HOSTNAME = {
    "hs103": "TP-Link HS103",
    "hs105": "TP-Link HS105",
    "ep25": "TP-Link EP-25",
    "tp25": "TP-Link TP-25",
}


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
        model = SMARTPLUG_MODELS_BY_HOSTNAME.get(device.get("hostname"))
        if model is None:
            continue
        device["type"] = SMARTPLUG_TYPE
        device["model"] = model
        print(f"Updated {device['mac']} -> type = '{SMARTPLUG_TYPE}', model = '{model}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
