# netscanner

Enumerates devices with current DHCP leases across all networks on a pfSense box, over SSH, and prints JSON.

Reads Kea DHCP's lease memfile (`/var/lib/kea/dhcp4.leases`) directly, since pfSense CE has no built-in REST API. A lease is only reported as `active` if it is genuinely unexpired right now — Kea's own `state` column lags reality (it's only flipped by periodic reclamation, not the instant a lease expires), so validity is computed from the `expire` timestamp instead. A lease that expired recently — within one more lease cycle — is reported as `stale` rather than dropped outright, since some devices (certain smart-home gear in particular) keep working fine long past their official expiry without proactively renewing. Leases expired longer than that are treated as gone. Reservation metadata (hostname, description) comes from `config.xml`, since it has richer data than Kea's generated config.

Kea's Lease File Cleanup (LFC) periodically compacts `dhcp4.leases` and keeps the prior file around as `dhcp4.leases.2`. A lease write racing that compaction can occasionally be dropped from the new file even though it's still genuinely valid — invisible until the device's next renewal. Since the goal here is discovering what's on the network (not auditing DHCP bookkeeping), `netscanner` also reads `dhcp4.leases.2` and recovers any lease missing from the current file, with the current file always taking precedence when both have a record for the same address. Disable with `--no-include-backup-leases` if you want strict current-file-only behavior.

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

Other flags: `--user`, `--port`, `--leases-path`, `--config-path`, `--include-backup-leases`, `-o/--output`, `--compact`. Run `uv run netscanner --help` for the full list.

## Enrichment

`netscanner`'s raw output only knows what pfSense knows — MAC, IP, hostname, and whatever description was set on a DHCP reservation. The `enrich` package fills in `type`/`model`/`description` for device families pfSense can't identify on its own, by cross-referencing external inventory dumps (Ring, Sonos) or simple hostname matching (Eero).

Each script reads a netscanner JSON document — as a file path argument, or from stdin if the argument is omitted — and writes the updated JSON to stdout, so they compose into a pipeline. Progress and per-device match messages go to stderr, keeping stdout clean for piping.

- `update-ring-devices <netscanner.json> data/ring_devices.txt` — matches Ring devices by MAC against `data/ring_devices.txt` (a pasted-in listing of your Ring device inventory). Sets `description` to `"Ring: <Name>"`, `type` to `Audio / Video Security System`, `model` to `Ring Security Device`.
- `update-sonos-devices <netscanner.json> data/sonos_system.txt` — matches Sonos speakers by MAC against `data/sonos_system.txt` (a pasted-in Sonos "About My System" diagnostic dump). Sets `description` to `"Sonos: <Room>: <Product>"`, `type` to `Wireless Speaker`, `model` to `Sonos Wireless Home Sound System`.
- `update-eero-devices <netscanner.json>` — matches devices with `hostname == "eero"`; no external inventory needed. Sets `type` to `Wireless Range Extender`, `model` to `Eero WiFi System`.
- `update-printer-devices <netscanner.json>` — matches known printers by hostname (`officeprinter` → Brother Printer/Scanner, `npifb72b6.stratford.` → HP Printer/Scanner); no external inventory needed. Sets `type` to `Printer/Scanner` and `model` accordingly.
- `update-floorheater-devices <netscanner.json>` — matches the device with `hostname == "floorheatt-stat"`; no external inventory needed. Sets `type` to `Floorheater`, `model` to `Schluter Thermostat`.
- `update-pc-devices <netscanner.json>` — matches known PCs by hostname (`jasons-mbp` → MacBook Pro, `thelio` → System76 Workstation, `cachyos-imac` → iMac); no external inventory needed. Sets `type` to `PC` and `model` accordingly.
- `update-appletv-devices <netscanner.json>` — matches known Apple TVs by hostname (`guest-bedroom`, `k--j-apple-tv`, `den`); no external inventory needed. Sets `type` to `Smart TV`, `model` to `Apple TV`.
- `update-pictureframe-devices <netscanner.json>` — matches the electronic picture frame by MAC (`04:c2:9b:1b:0f:2e`); no external inventory needed. Sets `type` to `Picture Frame`, `model` to `Aura`.
- `update-garagedoor-devices <netscanner.json>` — matches the device with `hostname == "myq-7ee"`; no external inventory needed. Sets `type` to `Garage Door`, `model` to `MyQ-7EE`.
- `update-arlo-devices <netscanner.json>` — matches the device with `hostname == "arloq"`; no external inventory needed. Sets `type` to `Audio / Video Security System`, `model` to `Arlo`.
- `update-echo-devices <netscanner.json>` — matches known Amazon Echo devices by MAC (`44:00:49:74:f7:68`, `fc:a1:83:ad:7c:83`, `a0:d0:dc:01:21:e1`); no external inventory needed. Sets `type` to `Smart Speaker`, `model` to `Amazon Echo`.
- `update-networking-devices <netscanner.json>` — matches known networking devices by hostname (`distribution-switch`, `access-switch` → TP-Link switch; `linksys00440` → Linksys WiFi Router); no external inventory needed. Sets `type` to `Networking Device` and `model` accordingly.
- `update-smartplug-devices <netscanner.json>` — matches known TP-Link smart plugs by hostname (`hs103` → TP-Link HS103, `hs105` → TP-Link HS105); no external inventory needed. Sets `type` to `Smart Plug` and `model` accordingly.
- `update-roomba-devices <netscanner.json>` — matches the device with `hostname == "irobot-105e11ff70874ae1abef649dbd67315a"`; no external inventory needed. Sets `type` to `Robot Vacuum`, `model` to `iRobot Roomba`.
- `update-lxc-devices <netscanner.json>` — matches known Proxmox LXC containers by hostname (`budgetbuddy-slack-app`, `winebuddy-slack-app`, `winebuddy-sync-with-cellartracker`, `twingate-connector`); no external inventory needed. Sets `type` to `LXC Container`, `model` to `Proxmox LXC Container`.
- `update-reolink-devices <netscanner.json>` — matches the device with `hostname == "office-camera"`; no external inventory needed. Sets `type` to `Surveillance Camera`, `model` to `Reolink Video Surveillance System`.
- `initialize-type-model-attributes <netscanner.json>` — run last; adds an empty `""` `type`/`model` to any device the earlier steps didn't touch, so every device ends up with both fields.

Any device from `data/*.txt` not found in the netscanner JSON (e.g. an inactive lease) is reported to stderr and skipped, rather than failing the run.

Run the full pipeline by hand:

```
cat expected.json |
  uv run update-ring-devices data/ring_devices.txt |
  uv run update-sonos-devices data/sonos_system.txt |
  uv run update-eero-devices |
  uv run update-printer-devices |
  uv run update-floorheater-devices |
  uv run update-pc-devices |
  uv run update-appletv-devices |
  uv run update-pictureframe-devices |
  uv run update-garagedoor-devices |
  uv run update-arlo-devices |
  uv run update-echo-devices |
  uv run update-networking-devices |
  uv run update-smartplug-devices |
  uv run update-roomba-devices |
  uv run update-lxc-devices |
  uv run update-reolink-devices |
  uv run initialize-type-model-attributes \
    >enriched.json
```

`generate_expected.sh` wraps both the scan and this pipeline end to end.

## Known limitations

- IPv4 only — DHCPv6 leases (`dhcp6.leases`) are not read.
- Assumes a Kea DHCP backend (pfSense's current default). Legacy ISC dhcpd (`dhcpd.leases`) is not supported.
