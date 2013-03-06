# -*- coding: utf-8 -*-

from oslo.config import cfg
from openstack.common import rpc

__all__ = ('parse_args', )


def parse_args(argv, default_config_files=None):
    rpc.set_defaults(control_exchange='forest')
    cfg.CONF(argv[1:], project='forest',
             default_config_files=default_config_files)


# TODO Simple test, REMOVE!
if __name__ == '__main__':
    import sys
    parse_args(sys.argv)
    print cfg.CONF
