# -*- coding: utf-8 -*-

import uuid

from openstack.common import log as logging
from openstack.common import exception

LOG = logging.getLogger(__name__)

def generate_request_id():
    return 'forest-req-' + str(uuid.uuid4())


class RequestContext(object):

    def __init__(self, auth_token=None, user=None, tenant=None, is_admin=False,
                 read_only=False, show_deleted=False, service_catalog=None):
        self.auth_token = auth_token
        self.user = user
        self.tenant = tenant
        self.is_admin = is_admin
        self.read_only = read_only
        self.show_deleted = show_deleted
        self.request_id = generate_request_id()
        self.service_catalog = service_catalog

    def to_dict(self):
        return {'user': self.user,
                'tenant': self.tenant,
                'is_admin': self.is_admin,
                'read_only': self.read_only,
                'show_deleted': self.show_deleted,
                'auth_token': self.auth_token,
                'request_id': self.request_id,
                'service_catalog': self.service_catalog}

    def get_endpoint(self, service_type, region=None, type='publicURL'):
        endpoints = getattr(self, '_endpoints', None)

        if endpoints is None:
            endpoints = {}
            for info in self.service_catalog:
                type_name = info.get('type')
                if type_name is None:
                    continue
                service = endpoints.setdefault(type_name, {})

                for ep in info['endpoints']:
                    region = ep['region']
                    service_region = service.get(region)
                    if service_region is not None:
                        # This is a second match, abort
                        raise exception.Duplicate('service type %s, region %s '
                            'is duplicated' % (type_name, service_region))
                    service[region] = ep

            self._endpoints = endpoints

        try:
            endpoint = self._endpoints[service_type][region][type]
        except KeyError:
            raise exception.NotFound('Endpoint (service_type %s, region %s, '
                'type %s) is not found' % ( type_name, service_type, type))
        return endpoint


def get_admin_context(show_deleted="no"):
    context = RequestContext(None,
                             tenant=None,
                             is_admin=True,
                             show_deleted=show_deleted)
    return context
