# -*- coding: utf-8 -*-

import functools

from oslo.config import cfg
from openstack.common import log as logging
from openstack.common.rpc import common as rpc_common

from forest.mapr import manager
from forest.mapr import rpcapi

mapr_opts = [
        cfg.BoolOpt('use_local',
                    default=True,
                    help='Perform forest.mapr operations locally'),
        cfg.StrOpt('topic',
                   default='mapr',
                   help='the topic mapr nodes listen on'),
        cfg.StrOpt('manager',
                   default='nova.forest.manager.MaprManager',
                   help='full class name for the Manager for Mapr'),
]

mapr_group = cfg.OptGroup(name='mapr',
                          title='Mapr Options')

CONF = cfg.CONF
CONF.register_group(mapr_group)
CONF.register_opts(mapr_opts, mapr_group)

LOG =  logging.getLogger(__name__)


class ExceptionHelper(object):
    """
    Using it in Local API. Class to wrap another and translate the
    ClientExceptions raised by its function calls to the actual ones.
    """

    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        func = getattr(self._target, name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except rpc_common.ClientException, e:
                raise (e._exc_info[1], None, e._exc_info[2])
        return wrapper


class LocalAPI(object):
    """
    A local version of the mapr API that does database updates
    locally instead of via RPC.
    """

    def __init__(self):
        self.manager = ExceptionHelper(manager.MaprManager())

    def wait_until_ready(self, context, *args, **kwargs):
        # nothing to wait for in the local case
        pass

    def ping(self, context, arg, timeout=None):
        pass


class API(object):
    """
    Mapr API that does updates via RPC to the MaprManager.
    """

    def __init__(self):
        self.mapr_rpc = rpcapi.MaprAPI()

    def wait_until_ready(self, context, early_timeout=10, early_attempts=10):
        pass


