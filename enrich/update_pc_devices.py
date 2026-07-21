"""Update device attributes for known PCs in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path

PC_TYPE = "PC"

PC_MODELS_BY_HOSTNAME = {
    "jasons-mbp": "MacBook Pro",
    "thelio": "System76 Workstation",
    "meerkat": "System76 Workstation",
    "cachyos-imac": "iMac",
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
        model = PC_MODELS_BY_HOSTNAME.get(device.get("hostname"))
        if model is None:
            continue
        device["type"] = PC_TYPE
        device["model"] = model
        print(f"Updated {device['mac']} -> type = '{PC_TYPE}', model = '{model}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
