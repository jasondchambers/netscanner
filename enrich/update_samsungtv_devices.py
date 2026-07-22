"""Update device attributes for the Samsung Smart TV in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

SAMSUNGTV_TYPE = "Smart TV"
SAMSUNGTV_MODEL = "Samsung"


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
        if device.get("mac") != "f8:04:2e:86:77:7a":
            continue
        device["type"] = SAMSUNGTV_TYPE
        device["model"] = SAMSUNGTV_MODEL
        print(f"Updated {device['mac']} -> type = '{SAMSUNGTV_TYPE}', model = '{SAMSUNGTV_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
