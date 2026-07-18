import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone

# Kea lease states (see Kea lease_state enum in lease.h)
STATE_DEFAULT = 0  # usable
STATE_DECLINED = 1
STATE_EXPIRED_RECLAIMED = 2


@dataclass
class Lease:
    ip: str
    mac: str | None
    hostname: str | None
    client_id: str | None
    kea_state: int
    valid_lifetime: int
    expire_epoch: int

    @property
    def expire_iso(self) -> str:
        return datetime.fromtimestamp(self.expire_epoch, tz=timezone.utc).isoformat()

    @property
    def last_renewed_iso(self) -> str:
        return datetime.fromtimestamp(self.expire_epoch - self.valid_lifetime, tz=timezone.utc).isoformat()

    def is_currently_valid(self, now_epoch: float) -> bool:
        return self.kea_state == STATE_DEFAULT and self.expire_epoch > now_epoch


def parse_leases(csv_text: str) -> dict[str, Lease]:
    """Parse a Kea memfile lease CSV (dhcp4.leases). Keeps the last row per address,
    since the memfile is an append-only log between Lease File Cleanup (LFC) compactions.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    latest: dict[str, Lease] = {}
    for row in reader:
        ip = row.get("address")
        if not ip:
            continue
        hwaddr = (row.get("hwaddr") or "").lower() or None
        hostname = (row.get("hostname") or "").strip() or None
        client_id = (row.get("client_id") or "").strip() or None
        try:
            valid_lifetime = int(row.get("valid_lifetime") or 0)
            expire_epoch = int(row.get("expire") or 0)
            kea_state = int(row.get("state") or 0)
        except ValueError:
            continue
        latest[ip] = Lease(
            ip=ip,
            mac=hwaddr,
            hostname=hostname,
            client_id=client_id,
            kea_state=kea_state,
            valid_lifetime=valid_lifetime,
            expire_epoch=expire_epoch,
        )
    return latest
