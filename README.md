# netscanner

Discovers devices on a pfSense network by reading DHCP leases over SSH, then enriches the results by filling in a `type` and `model` for devices pfSense can't identify on its own.

## Setup

1. A dedicated SSH key must be authorized for `root` on the pfSense box (System → User Manager → root → Authorized SSH Keys).
2. Point the tool at your key and host, either via flags or env vars:

```
export PFSENSE_HOST=10.27.27.1
export PFSENSE_SSH_KEY=~/.ssh/netscanner_pfsense
```

## Usage

```
./generate_expected.sh
```

This is the main entry point. It scans the network and writes the raw device list to `expected.json`, then runs it through the `enrich` package to produce `enriched.json` — the same devices, with `type`/`model` (and sometimes `description`) filled in wherever a device is recognized by hostname or MAC address. Edit the script if your pfSense host differs from `10.27.27.1`.

To run just the scan, without enrichment:

```
uv run netscanner --host 10.27.27.1
```

Run `uv run netscanner --help` for the full list of flags.

## Known limitations

- IPv4 only — DHCPv6 leases (`dhcp6.leases`) are not read.
- Assumes a Kea DHCP backend (pfSense's current default). Legacy ISC dhcpd (`dhcpd.leases`) is not supported.
