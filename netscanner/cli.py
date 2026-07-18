import argparse
import json
import os
import sys
from datetime import datetime, timezone

from netscanner.devices import build_devices
from netscanner.leases import parse_leases
from netscanner.pfsense_config import parse_config
from netscanner.ssh import SSHConfig, fetch_file

DEFAULT_LEASES_PATH = "/var/lib/kea/dhcp4.leases"
DEFAULT_CONFIG_PATH = "/cf/conf/config.xml"
DEFAULT_KEY_PATH = "~/.ssh/netscanner_pfsense"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netscanner",
        description="Enumerate devices with current DHCP leases across all pfSense networks.",
    )
    parser.add_argument("--host", default=os.environ.get("PFSENSE_HOST"), help="pfSense hostname or IP (env: PFSENSE_HOST)")
    parser.add_argument("--user", default=os.environ.get("PFSENSE_USER", "root"), help="SSH user (env: PFSENSE_USER, default: root)")
    parser.add_argument("--key", default=os.environ.get("PFSENSE_SSH_KEY", DEFAULT_KEY_PATH), help="SSH private key path (env: PFSENSE_SSH_KEY)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PFSENSE_SSH_PORT", 22)), help="SSH port (env: PFSENSE_SSH_PORT, default: 22)")
    parser.add_argument("--leases-path", default=DEFAULT_LEASES_PATH, help="Remote path to Kea's dhcp4.leases memfile")
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH, help="Remote path to pfSense config.xml")
    parser.add_argument(
        "--include-offline-reservations",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Also include static DHCP reservations that have no active lease right now (default: on; use --no-include-offline-reservations for active leases only)",
    )
    parser.add_argument("-o", "--output", help="Write JSON to this file instead of stdout")
    parser.add_argument("--compact", action="store_true", help="Emit compact single-line JSON instead of pretty-printed")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if not args.host:
        parser.error("--host is required (or set PFSENSE_HOST)")

    ssh_cfg = SSHConfig(host=args.host, user=args.user, key_path=args.key, port=args.port)

    try:
        leases_text = fetch_file(ssh_cfg, args.leases_path)
        config_text = fetch_file(ssh_cfg, args.config_path)
    except Exception as exc:
        print(f"netscanner: {exc}", file=sys.stderr)
        return 1

    leases = parse_leases(leases_text)
    interfaces, static_maps = parse_config(config_text)
    devices = build_devices(leases, interfaces, static_maps, include_offline_reservations=args.include_offline_reservations)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pfsense_host": args.host,
        "networks": [
            {"interface": i.ifname, "description": i.description, "network": i.network}
            for i in interfaces
            if i.network
        ],
        "device_count": len(devices),
        "devices": devices,
    }

    text = json.dumps(result, indent=None if args.compact else 2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(text + "\n")
    else:
        print(text)

    return 0
