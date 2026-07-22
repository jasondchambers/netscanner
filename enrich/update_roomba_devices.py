"""Update device attributes for the iRobot Roomba in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

ROOMBA_TYPE = "Robot Vacuum"
ROOMBA_MODEL = "iRobot Roomba"


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
        if device.get("hostname") != "irobot-105e11ff70874ae1abef649dbd67315a":
            continue
        device["type"] = ROOMBA_TYPE
        device["model"] = ROOMBA_MODEL
        print(f"Updated {device['mac']} -> type = '{ROOMBA_TYPE}', model = '{ROOMBA_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
