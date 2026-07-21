"""Update device attributes for Ring devices in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import re
import sys
from pathlib import Path

RING_TYPE = "Audio / Video Security System"
RING_MODEL = "Ring Security Device"


def parse_ring_devices(path: Path) -> list[dict]:
    devices = []
    lines = path.read_text().splitlines()
    for line in lines:
        match = re.match(
            r"^(?P<name>.+?)\s{2,}(?P<kind>\S+)\s+(?P<mac>[0-9a-fA-F:]{17})\s+(?P<status>\S+)\s*$",
            line,
        )
        if match:
            devices.append(
                {
                    "name": match.group("name").strip(),
                    "kind": match.group("kind"),
                    "mac": match.group("mac").lower(),
                    "status": match.group("status"),
                }
            )
    return devices


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "expected_json",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the netscanner JSON file (reads from stdin if omitted)",
    )
    parser.add_argument("ring_devices_txt", type=Path, help="Path to the Ring device inventory text file")
    args = parser.parse_args()

    ring_devices = parse_ring_devices(args.ring_devices_txt)
    if args.expected_json is None:
        data = json.load(sys.stdin)
        source_label = "stdin"
    else:
        data = json.loads(args.expected_json.read_text())
        source_label = args.expected_json

    devices_by_mac = {d["mac"].lower(): d for d in data["devices"]}

    for ring_device in ring_devices:
        mac = ring_device["mac"]
        name = ring_device["name"]
        device = devices_by_mac.get(mac)
        if device is None:
            print(f"NOT FOUND: Ring device '{name}' ({mac}) not present in {source_label}", file=sys.stderr)
            continue
        device["description"] = f"Ring: {name}"
        device["type"] = RING_TYPE
        device["model"] = RING_MODEL
        print(f"Updated {mac} -> description = 'Ring: {name}', type = '{RING_TYPE}', model = '{RING_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
