# -*- coding: utf-8 -*-

import netaddr


class LazyPluggable(object):
    ''' A pluggable backend loaded lazily based on some value. '''

    def __init__(self, pivot, config_group=None, **backends):
        self._backends = backends
        self._pivot = pivot
        self._backend = None
        self._config_group = config_group

    def _get_backend(self):
        if not self._backend:
            if self._config_group is None:
                backend_name = CONF[self._pivot]
            else:
                backend_name = CONF[self._config_group][self._pivot]

            if backend_name not in self._backends:
                raise except.




def is_valid_ipv4(address):
    ''' Verify that address represents a valid IPv4 address '''
    try:
        return netaddr.valid_ipv4(address)
    except Exception:
        return False


def is_valid_ipv6(address):
    ''' Verify that address represents a valid IPv6 address '''
    try:
        return netaddr.valid_ipv6(address)
    except Exception:
        return False


def is_valid_ipv6_cidr(address):
    try:
        str(netaddr.IPNetwork(address, version=6).cidr)
        return True
    except Exception:
        return False


def get_shortened_ipv6(address):
    addr = netaddr.IPAddress(address, version=6)
    return str(addr.ipv6())


def get_shortened_ipv6_cidr(address):
    net = netaddr.IPNetwork(address, version=6)
    return str(net.cidr)


def is_valid_cidr(address):
    """Check if the provided ipv4 or ipv6 address is a valid
    CIDR address or not"""
    try:
        # Validate the correct CIDR Address
        netaddr.IPNetwork(address)
    except netaddr.core.AddrFormatError:
        return False
    except UnboundLocalError:
        # NOTE(MotoKen): work around bug in netaddr 0.7.5 (see detail in
        # https://github.com/drkjam/netaddr/issues/2)
        return False

    # Prior validation partially verify /xx part
    # Verify it here
    ip_segment = address.split('/')

    if (len(ip_segment) <= 1 or
        ip_segment[1] == ''):
        return False

    return True
