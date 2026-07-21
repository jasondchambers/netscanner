"""Initialize missing type/model attributes on devices in a netscanner JSON file to empty strings, writing the result to stdout."""

import argparse
import json
import sys
from pathlib import Path


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

    updated = 0
    for device in data["devices"]:
        added = []
        if "type" not in device:
            device["type"] = ""
            added.append("type")
        if "model" not in device:
            device["model"] = ""
            added.append("model")
        if added:
            updated += 1
            print(f"Initialized {device['mac']} -> {', '.join(added)}", file=sys.stderr)

    print(f"Updated {updated} device(s)", file=sys.stderr)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
