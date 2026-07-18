import ipaddress
import time

from netscanner.leases import Lease
from netscanner.pfsense_config import NetworkInterface, StaticMapping


def _locate_interface(ip: str, interfaces: list[NetworkInterface]) -> NetworkInterface | None:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    for iface in interfaces:
        if iface.network and addr in ipaddress.ip_network(iface.network):
            return iface
    return None


def _device_record(
    *,
    mac: str | None,
    ip: str | None,
    hostname: str | None,
    description: str | None,
    client_id: str | None,
    is_static_reservation: bool,
    status: str,
    lease_last_renewed: str | None,
    lease_expires: str | None,
    iface: NetworkInterface | None,
    fallback_ifname: str | None = None,
) -> dict:
    return {
        "mac": mac,
        "ip": ip,
        "hostname": hostname,
        "description": description,
        "client_id": client_id,
        "is_static_reservation": is_static_reservation,
        "status": status,
        "lease_last_renewed": lease_last_renewed,
        "lease_expires": lease_expires,
        "interface": iface.ifname if iface else fallback_ifname,
        "interface_description": iface.description if iface else None,
        "network": iface.network if iface else None,
    }


def build_devices(
    leases: dict[str, Lease],
    interfaces: list[NetworkInterface],
    static_maps: list[StaticMapping],
    include_offline_reservations: bool = False,
    now_epoch: float | None = None,
) -> list[dict]:
    if now_epoch is None:
        now_epoch = time.time()

    static_by_mac = {s.mac: s for s in static_maps}
    iface_by_name = {i.ifname: i for i in interfaces}

    devices = []
    seen_macs: set[str] = set()

    for ip, lease in leases.items():
        if not lease.is_currently_valid(now_epoch):
            continue

        iface = _locate_interface(ip, interfaces)
        static = static_by_mac.get(lease.mac) if lease.mac else None

        devices.append(
            _device_record(
                mac=lease.mac,
                ip=ip,
                hostname=lease.hostname or (static.hostname if static else None),
                description=static.description if static else None,
                client_id=lease.client_id,
                is_static_reservation=static is not None,
                status="active",
                lease_last_renewed=lease.last_renewed_iso,
                lease_expires=lease.expire_iso,
                iface=iface,
            )
        )
        if lease.mac:
            seen_macs.add(lease.mac)

    if include_offline_reservations:
        for s in static_maps:
            if s.mac in seen_macs:
                continue
            devices.append(
                _device_record(
                    mac=s.mac,
                    ip=s.ip or None,
                    hostname=s.hostname,
                    description=s.description,
                    client_id=None,
                    is_static_reservation=True,
                    status="reserved_no_active_lease",
                    lease_last_renewed=None,
                    lease_expires=None,
                    iface=iface_by_name.get(s.interface),
                    fallback_ifname=s.interface,
                )
            )

    def sort_key(d: dict):
        try:
            ip_key = int(ipaddress.ip_address(d["ip"]))
        except (TypeError, ValueError):
            ip_key = -1
        return (d["interface"] or "", ip_key)

    devices.sort(key=sort_key)
    return devices
