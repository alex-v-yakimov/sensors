import os
import sys
import socket
import signal
import struct
import configargparse
from ipaddress import ip_address, IPv6Address
import sensors.common.const as const
from sensors.common.common import (
    type_ip_port,
    type_mcast_group,
    logger,
    SystemdStopInterrupt,
    raise_systemd_stop_interrupt
)

signal.signal(signal.SIGTERM, raise_systemd_stop_interrupt)


def get_conf() -> configargparse.Namespace:
    parser = configargparse.ArgumentParser(
        prog='receiver',
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
        '--sensors_log_file',
        type=str,
        default=const.SENSORS_LOG_FILE,
        help='Sensors Log File'
    )
    conf = parser.parse_args()
    return conf


def get_socket(conf: configargparse.Namespace) -> socket.socket:
    if isinstance(conf.mcast_group, IPv6Address):
        family = socket.AF_INET6
        mreq = struct.pack('16sI', conf.mcast_group.packed, 0)
        ipproto_args = (socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
    else:
        family = socket.AF_INET
        mreq = struct.pack('4sI', conf.mcast_group.packed, 0)
        ipproto_args = (socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock = socket.socket(family, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', conf.mcast_port))
    sock.setsockopt(*ipproto_args)
    return sock


def run_loop(conf: configargparse.Namespace, sock: socket.socket) -> None:
    try:
        with open(conf.sensors_log_file, 'a') as fh:
            while True:
                try:
                    data = sock.recv(const.BUFFER_SIZE).decode(encoding='utf-8')
                    fh.write(data + '\n')
                    fh.flush()
                except KeyboardInterrupt:
                    print()
                    sock.close()
                    break
                except SystemdStopInterrupt:
                    sock.close()
                    break
    except IOError as err:
        logger.error(err)
        sys.exit(os.EX_IOERR)


def main() -> None:
    conf = get_conf()
    sock = get_socket(conf)
    run_loop(conf, sock)
