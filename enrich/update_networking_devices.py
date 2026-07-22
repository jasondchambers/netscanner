"""Update device attributes for networking devices in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

NETWORKING_TYPE = "Networking Device"

NETWORKING_MODELS_BY_HOSTNAME = {
    "distribution-switch": "TP-Link switch",
    "access-switch": "TP-Link switch",
    "linksys00440": "Linksys WiFi Router",
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
        model = NETWORKING_MODELS_BY_HOSTNAME.get(device.get("hostname"))
        if model is None:
            continue
        device["type"] = NETWORKING_TYPE
        device["model"] = model
        print(f"Updated {device['mac']} -> type = '{NETWORKING_TYPE}', model = '{model}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
