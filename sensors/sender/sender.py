import os
import sys
import time
import socket
import signal
import configargparse
import subprocess
import json
from datetime import datetime
from ipaddress import ip_address, IPv6Address
import sensors.common.const as const
from sensors.common.common import (
    type_ip_port,
    type_mcast_group,
    type_ip_ttl,
    logger,
    raise_systemd_stop_interrupt,
    SystemdStopInterrupt
)

hostname = socket.gethostname()

signal.signal(signal.SIGTERM, raise_systemd_stop_interrupt)


def get_conf() -> configargparse.Namespace:
    parser = configargparse.ArgumentParser(
        prog='sender',
        description='Sensors Log Receiver',
        args_for_setting_config_path=['-c', '--c'],
        config_arg_help_message='config file'
    )
    parser.add_argument(
        '--mcast_group',
        type=type_mcast_group,
        default=ip_address(const.MCAST_GROUP),
        help='MultiCast Group'
    )
    parser.add_argument(
        '--mcast_port',
        type=type_ip_port,
        default=const.MCAST_PORT,
        help='MultiCast Port'
    )
    parser.add_argument(
        '--mcast_ttl',
        type=type_ip_ttl,
        default=const.MCAST_TTL,
        help='MultiCast TTL'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=const.INTERVAL,
        help='Interval in seconds'
    )
    parser.add_argument(
        '--sensors_command',
        type=str,
        default=const.SENSORS_COMMAND,
        help='Sensors Command'
    )
    conf = parser.parse_args()
    return conf


def get_socket(conf: configargparse.Namespace) -> socket.socket:
    if isinstance(conf.mcast_group, IPv6Address):
        family = socket.AF_INET6
        ipproto_args = (socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, conf.mcast_ttl)
    else:
        family = socket.AF_INET
        ipproto_args = (socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, conf.mcast_ttl)

    sock = socket.socket(family, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(*ipproto_args)
    return sock


def get_sensors(cmd: str) -> bytes:
    try:
        stdout = subprocess.check_output(cmd, shell=True)
        data = json.loads(stdout)
        data['hostname'] = hostname
        data['date'] = str(datetime.now())
        return json.dumps(data, separators=(',', ':')).encode()
    except (subprocess.CalledProcessError, json.decoder.JSONDecodeError) as err:
        logger.error(err)
        sys.exit(os.EX_IOERR)


def run_loop(conf: configargparse.Namespace, sock: socket.socket) -> None:
    while True:
        try:
            sock.sendto(get_sensors(conf.sensors_command), (str(conf.mcast_group), conf.mcast_port))
            time.sleep(conf.interval)
        except KeyboardInterrupt:
            print()
            break
        except SystemdStopInterrupt:
            break


def main() -> None:
    conf = get_conf()
    sock = get_socket(conf)
    run_loop(conf, sock)
