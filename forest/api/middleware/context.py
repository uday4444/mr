# -*- coding: utf-8 -*-

from oslo.config import cfg
import webob.exc

import openstack.common.jsonutils as json
import openstack.common.log as logging
import openstack.common.wsgi

import forest.common.context as context

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

context_opts = [
    cfg.BoolOpt('owner_is_tenant', default=True),
    cfg.StrOpt('admin_role', default='admin'),
    cfg.BoolOpt('allow_anonymous_access', default=False),
]
CONF.register_opts(context_opts)


class BaseContextMiddleware(openstack.common.wsgi.Middleware):

    def __init__(self, app, global_conf, **local_conf):
        super(BaseContextMiddleware, self).__init__(app)

    def _get_anonymous_context(self):
        return context.get_admin_context()

    def process_response(self, resp):
        try:
            request_id = resp.request.context.request_id
        except AttributeError:
            LOG.warn('Unable to retrieve request id from context')
        else:
            resp.headers['x-openstack-request-id'] = request_id
        return resp


class ContextMiddleware(BaseContextMiddleware):

    def process_request(self, req):
        '''
        Convert authentication information into a request context

        :param req: wsgi request object that will be given the context object
        :raises webob.exc.HTTPUnauthorized: when value of the X-Identity-Status
                                            header is not 'Confirmed' and
                                            anonymous access is disallowed
        '''
        if req.headers.get('X-Identity-Status') == 'Confirmed':
            req.context = self._get_authenticated_context(req)
        elif CONF.allow_anonymous_access:
            req.context = self._get_anonymous_context()
        else:
            raise webob.exc.HTTPUnauthorized()
        return None


    def _get_authenticated_context(self, req):

        headers = req.headers

        deprecated_token = headers.get('X-Storage-Token')
        roles_header = headers.get('X-Roles', '') # X-Roles is a csv string
        roles = [r.strip().lower() for r in roles_header.split(',')]

        catalog_header = headers.get('X-Service-Catalog')
        if catalog_header is not None:
            try:
                service_catalog = json.loads(catalog_header)
            except ValueError:
                raise webob.exc.HTTPInternalServerError('Invalid server '
                                                        'catalog json')

        kwargs = {
            'auth_token': headers.get('X-Auth-Token', deprecated_token),
            'user': req.headers.get('X-User-Id'),
            'tenant': req.headers.get('X-Tenant-Id'),
            'is_admin': CONF.admin_role.strip().lower() in roles,
            'service_catalog': service_catalog,
        }

        return context.RequestContext(**kwargs)


class UnauthenticatedContextMiddleware(BaseContextMiddleware):

    def process_request(self, req):
        req.context = self._get_anonymous_context()
        return None
