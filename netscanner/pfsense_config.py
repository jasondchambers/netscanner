import ipaddress
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class NetworkInterface:
    ifname: str  # pfSense internal name, e.g. "opt2"
    if_device: str | None  # e.g. "igb1.10"
    description: str | None  # e.g. "IoT"
    network: str | None  # CIDR, e.g. "172.20.0.0/23"


@dataclass
class StaticMapping:
    mac: str
    ip: str
    hostname: str | None
    description: str | None
    interface: str  # pfSense ifname this reservation belongs to


def parse_config(xml_text: str) -> tuple[list[NetworkInterface], list[StaticMapping]]:
    root = ET.fromstring(xml_text)

    interfaces = []
    interfaces_el = root.find("interfaces")
    if interfaces_el is not None:
        for iface_el in interfaces_el:
            ipaddr = iface_el.findtext("ipaddr")
            subnet = iface_el.findtext("subnet")
            network = None
            if ipaddr and subnet and ipaddr not in ("dhcp", "dhcp6", ""):
                try:
                    network = str(ipaddress.ip_network(f"{ipaddr}/{subnet}", strict=False))
                except ValueError:
                    network = None
            interfaces.append(
                NetworkInterface(
                    ifname=iface_el.tag,
                    if_device=iface_el.findtext("if") or None,
                    description=iface_el.findtext("descr") or None,
                    network=network,
                )
            )

    static_maps = []
    dhcpd_el = root.find("dhcpd")
    if dhcpd_el is not None:
        for iface_el in dhcpd_el:
            for sm in iface_el.findall("staticmap"):
                mac = (sm.findtext("mac") or "").lower()
                if not mac:
                    continue
                static_maps.append(
                    StaticMapping(
                        mac=mac,
                        ip=sm.findtext("ipaddr") or "",
                        hostname=sm.findtext("hostname") or None,
                        description=sm.findtext("descr") or None,
                        interface=iface_el.tag,
                    )
                )

    return interfaces, static_maps
