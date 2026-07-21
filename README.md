# netscanner

Enumerates devices with current DHCP leases across all networks on a pfSense box, over SSH, and prints JSON.

Reads Kea DHCP's lease memfile (`/var/lib/kea/dhcp4.leases`) directly, since pfSense CE has no built-in REST API. A lease is only reported as `active` if it is genuinely unexpired right now — Kea's own `state` column lags reality (it's only flipped by periodic reclamation, not the instant a lease expires), so validity is computed from the `expire` timestamp instead. A lease that expired recently — within one more lease cycle — is reported as `stale` rather than dropped outright, since some devices (certain smart-home gear in particular) keep working fine long past their official expiry without proactively renewing. Leases expired longer than that are treated as gone. Reservation metadata (hostname, description) comes from `config.xml`, since it has richer data than Kea's generated config.

## Setup

1. A dedicated SSH key must be authorized for `root` on the pfSense box (System → User Manager → root → Authorized SSH Keys).
2. Point the tool at your key and host, either via flags or env vars:

```
export PFSENSE_HOST=10.27.27.1
export PFSENSE_SSH_KEY=~/.ssh/netscanner_pfsense
```

## Usage

The easiest way to produce both the raw and enriched device inventory in one shot:

```
./generate_expected.sh
```

This runs `netscanner` against the pfSense host, writes the raw device list to `expected.json`, then pipes it through the enrichment pipeline (see [Enrichment](#enrichment)) to produce `enriched.json`. Edit the script if your pfSense host differs from `10.27.27.1`.

To run `netscanner` directly instead:

```
uv run netscanner --host 10.27.27.1
```

By default, devices with a currently unexpired lease are listed *plus* static DHCP reservations that have no active lease right now (common for long-uptime devices that haven't needed to renew since the last lease-file compaction). Use `--no-include-offline-reservations` to restrict output to genuinely active leases only:

```
uv run netscanner --host 10.27.27.1 --no-include-offline-reservations
```

Other flags: `--user`, `--port`, `--leases-path`, `--config-path`, `-o/--output`, `--compact`. Run `uv run netscanner --help` for the full list.

## Enrichment

`netscanner`'s raw output only knows what pfSense knows — MAC, IP, hostname, and whatever description was set on a DHCP reservation. The `enrich` package fills in `type`/`model`/`description` for device families pfSense can't identify on its own, by cross-referencing external inventory dumps (Ring, Sonos) or simple hostname matching (Eero).

Each script reads a netscanner JSON document — as a file path argument, or from stdin if the argument is omitted — and writes the updated JSON to stdout, so they compose into a pipeline. Progress and per-device match messages go to stderr, keeping stdout clean for piping.

- `update-ring-devices <netscanner.json> data/ring_devices.txt` — matches Ring devices by MAC against `data/ring_devices.txt` (a pasted-in listing of your Ring device inventory). Sets `description` to `"Ring: <Name>"`, `type` to `Audio / Video Security System`, `model` to `Ring Security Device`.
- `update-sonos-devices <netscanner.json> data/sonos_system.txt` — matches Sonos speakers by MAC against `data/sonos_system.txt` (a pasted-in Sonos "About My System" diagnostic dump). Sets `description` to `"Sonos: <Room>: <Product>"`, `type` to `Wireless Speaker`, `model` to `Sonos Wireless Home Sound System`.
- `update-eero-devices <netscanner.json>` — matches devices with `hostname == "eero"`; no external inventory needed. Sets `type` to `Wireless Range Extender`, `model` to `Eero WiFi System`.
- `initialize-type-model-attributes <netscanner.json>` — run last; adds an empty `""` `type`/`model` to any device the earlier steps didn't touch, so every device ends up with both fields.

Any device from `data/*.txt` not found in the netscanner JSON (e.g. an inactive lease) is reported to stderr and skipped, rather than failing the run.

Run the full pipeline by hand:

```
cat expected.json |
  uv run update-ring-devices data/ring_devices.txt |
  uv run update-sonos-devices data/sonos_system.txt |
  uv run update-eero-devices |
  uv run initialize-type-model-attributes \
    >enriched.json
```

`generate_expected.sh` wraps both the scan and this pipeline end to end.

## Known limitations

- IPv4 only — DHCPv6 leases (`dhcp6.leases`) are not read.
- Assumes a Kea DHCP backend (pfSense's current default). Legacy ISC dhcpd (`dhcpd.leases`) is not supported.
