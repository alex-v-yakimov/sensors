from typing import Union
import logging
from ipaddress import ip_address, IPv4Address, IPv6Address
import sensors.common.const as const

logging.basicConfig(format='%(levelname)s :: %(message)s')
logger = logging.getLogger(const.LOGGER_NAME)
logger.setLevel(const.LOG_LEVEL)


class SystemdStopInterrupt(Exception):
    pass


def raise_systemd_stop_interrupt(signum, frame):
    raise SystemdStopInterrupt


def type_ip_port(arg: str) -> int:
    if const.IP_PORT_MIN < (ip_port := int(arg)) < const.IP_PORT_MAX:
        return ip_port
    else:
        raise ValueError


def type_ip_ttl(arg: str) -> int:
    if const.IP_TTL_MIN < (ip_ttl := int(arg)) < const.IP_TTL_MAX:
        return ip_ttl
    else:
        raise ValueError


def type_mcast_group(arg: str) -> Union[IPv4Address, IPv6Address]:
    mcast_group = ip_address(arg)
    if mcast_group.is_multicast:
        return mcast_group
    else:
        raise ValueError
