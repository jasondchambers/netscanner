"""Update device attributes for Amazon Echo devices in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

ECHO_TYPE = "Smart Speaker"
ECHO_MODEL = "Amazon Echo"

ECHO_MACS = {"44:00:49:74:f7:68", "fc:a1:83:ad:7c:83", "a0:d0:dc:01:21:e1"}


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
        if device.get("mac") not in ECHO_MACS:
            continue
        device["type"] = ECHO_TYPE
        device["model"] = ECHO_MODEL
        print(f"Updated {device['mac']} -> type = '{ECHO_TYPE}', model = '{ECHO_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
