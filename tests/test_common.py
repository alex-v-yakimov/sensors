import pytest
from ipaddress import ip_address
from sensors.common.common import type_ip_ttl, type_ip_port, type_mcast_group


def test_type_ip_ttl():
    assert type_ip_ttl('44') == 44
    with pytest.raises(ValueError):
        type_ip_ttl('256')
    with pytest.raises(ValueError):
        type_ip_ttl('-1')


def test_type_ip_port():
    assert type_ip_port('20220') == 20220
    with pytest.raises(ValueError):
        type_ip_port('65536')
    with pytest.raises(ValueError):
        type_ip_port('1023')


def test_type_mcast_group():
    assert type_mcast_group('ff88::88') == ip_address('ff88::88')
    with pytest.raises(ValueError):
        type_mcast_group('192.168.1.1')
