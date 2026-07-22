"""Update device attributes for Proxmox LXC containers in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

LXC_TYPE = "LXC Container"
LXC_MODEL = "Proxmox LXC Container"

LXC_HOSTNAMES = {
    "budgetbuddy-slack-app",
    "winebuddy-slack-app",
    "winebuddy-sync-with-cellartracker",
    "twingate-connector",
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
        if device.get("hostname") not in LXC_HOSTNAMES:
            continue
        device["type"] = LXC_TYPE
        device["model"] = LXC_MODEL
        print(f"Updated {device['mac']} -> type = '{LXC_TYPE}', model = '{LXC_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
