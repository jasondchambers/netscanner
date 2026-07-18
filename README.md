# netscanner

Enumerates devices with current DHCP leases across all networks on a pfSense box, over SSH, and prints JSON.

Reads Kea DHCP's lease memfile (`/var/lib/kea/dhcp4.leases`) directly, since pfSense CE has no built-in REST API. A lease is only reported as `active` if it is genuinely unexpired right now — Kea's own `state` column lags reality (it's only flipped by periodic reclamation, not the instant a lease expires), so validity is computed from the `expire` timestamp instead. Reservation metadata (hostname, description) comes from `config.xml`, since it has richer data than Kea's generated config.

## Setup

1. A dedicated SSH key must be authorized for `root` on the pfSense box (System → User Manager → root → Authorized SSH Keys).
2. Point the tool at your key and host, either via flags or env vars:

```
export PFSENSE_HOST=10.27.27.1
export PFSENSE_SSH_KEY=~/.ssh/netscanner_pfsense
```

## Usage

```
uv run netscanner --host 10.27.27.1
```

By default, devices with a currently unexpired lease are listed *plus* static DHCP reservations that have no active lease right now (common for long-uptime devices that haven't needed to renew since the last lease-file compaction). Use `--no-include-offline-reservations` to restrict output to genuinely active leases only:

```
uv run netscanner --host 10.27.27.1 --no-include-offline-reservations
```

Other flags: `--user`, `--port`, `--leases-path`, `--config-path`, `-o/--output`, `--compact`. Run `uv run netscanner --help` for the full list.

## Known limitations

- IPv4 only — DHCPv6 leases (`dhcp6.leases`) are not read.
- Assumes a Kea DHCP backend (pfSense's current default). Legacy ISC dhcpd (`dhcpd.leases`) is not supported.
