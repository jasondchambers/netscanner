"""Update device attributes for the kitchen light in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

KITCHENLIGHT_TYPE = "Smart Light"
KITCHENLIGHT_MODEL = "Tuya Smart Light"


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
        if device.get("mac") != "d4:a6:51:49:b3:72":
            continue
        device["type"] = KITCHENLIGHT_TYPE
        device["model"] = KITCHENLIGHT_MODEL
        print(f"Updated {device['mac']} -> type = '{KITCHENLIGHT_TYPE}', model = '{KITCHENLIGHT_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
