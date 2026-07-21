"""Update device attributes for Sonos devices in a netscanner JSON file, writing the result to stdout."""

import argparse
import json
import re
import sys
from pathlib import Path

SONOS_TYPE = "Wireless Speaker"
SONOS_MODEL = "Sonos Wireless Home Sound System"

SEPARATOR_RE = re.compile(r"^-+$")
SERIAL_RE = re.compile(r"^Serial Number:\s*([0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5})")


def parse_sonos_devices(path: Path) -> list[dict]:
    devices = []
    blocks: list[list[str]] = [[]]
    for line in path.read_text().splitlines():
        if SEPARATOR_RE.match(line):
            blocks.append([])
        else:
            blocks[-1].append(line)

    for block in blocks:
        lines = [line for line in block if line.strip()]
        if not lines:
            continue

        header = lines[0]
        if ": " not in header:
            continue
        kind, name = header.split(": ", 1)

        mac = None
        for line in lines[1:]:
            match = SERIAL_RE.match(line)
            if match:
                mac = match.group(1).replace("-", ":").lower()
                break

        if mac is None:
            print(f"SKIPPED: '{header}' has no Serial Number/MAC address, skipping", file=sys.stderr)
            continue

        devices.append({"name": name.strip(), "kind": kind.strip(), "mac": mac})

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
    parser.add_argument("sonos_system_txt", type=Path, help="Path to the Sonos system inventory text file")
    args = parser.parse_args()

    sonos_devices = parse_sonos_devices(args.sonos_system_txt)
    if args.expected_json is None:
        data = json.load(sys.stdin)
        source_label = "stdin"
    else:
        data = json.loads(args.expected_json.read_text())
        source_label = args.expected_json

    devices_by_mac = {d["mac"].lower(): d for d in data["devices"]}

    for sonos_device in sonos_devices:
        mac = sonos_device["mac"]
        name = sonos_device["name"]
        device = devices_by_mac.get(mac)
        if device is None:
            print(f"NOT FOUND: Sonos device '{name}' ({mac}) not present in {source_label}", file=sys.stderr)
            continue
        kind = sonos_device["kind"]
        description = f"Sonos: {name}: {kind}"
        device["description"] = description
        device["type"] = SONOS_TYPE
        device["model"] = SONOS_MODEL
        print(f"Updated {mac} -> description = '{description}', type = '{SONOS_TYPE}', model = '{SONOS_MODEL}'", file=sys.stderr)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
