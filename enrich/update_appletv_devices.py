"""Update device attributes for Apple TVs in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

APPLETV_TYPE = "Smart TV"
APPLETV_MODEL = "Apple TV"

APPLETV_HOSTNAMES = {"guest-bedroom", "k--j-apple-tv", "den"}


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
        if device.get("hostname") not in APPLETV_HOSTNAMES:
            continue
        device["type"] = APPLETV_TYPE
        device["model"] = APPLETV_MODEL
        print(f"Updated {device['mac']} -> type = '{APPLETV_TYPE}', model = '{APPLETV_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
