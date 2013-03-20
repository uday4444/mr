# -*- coding: utf-8 -*-

from oslo.config import cfg
import openstack.common.rpc.proxy
#from openstack.common import jsonutils

CONF = cfg.CONF

class MaprAPI(openstack.common.rpc.proxy):
    ''' Client side of the mapr '''

    BASE_RPC_API_VERSION = '1.0'

    def __init__(self):
        super(MaprAPI, self).__init__(
            topic=CONF.mapr.topic,
            default_version=self.BASE_RPC_API_VERSION)
