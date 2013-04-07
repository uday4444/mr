import json

from oslo.config import cfg
import webob.exc

import openstack.common.log as logging
import openstack.common.context
import forest.common.wsgi

context_opts = [
    cfg.BoolOpt('owner_is_tenant', default=True),
    cfg.StrOpt('admin_role', default='admin'),
    cfg.BoolOpt('allow_anonymous_access', default=False),
]

CONF = cfg.CONF
CONF.register_opts(context_opts)

LOG = logging.getLogger(__name__)


class BaseContextMiddleware(forest.common.wsgi.Middleware):

    def process_response(self, resp):
        try:
            request_id = resp.request.context.request_id
        except AttributeError:
            LOG.warn('Unable to retrieve request id from context')
        else:
            resp.headers['x-openstack-request-id'] = 'req-%s' % request_id
        return resp


def _get_anonymous_context():
    return openstack.common.context.get_admin_context()


class ContextMiddleware(BaseContextMiddleware):

    def process_request(self, req):
        '''
        Convert authentication information into a request context

        Generate a forest.context.RequestContext object from the available
        authentication headers and store on the 'context' attribute
        of the req object.

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


    def _get_authenticated_context(self, req):
        #NOTE(bcwaldon): X-Roles is a csv string, but we need to parse
        # it into a list to be useful
        roles_header = req.headers.get('X-Roles', '')
        roles = [r.strip().lower() for r in roles_header.split(',')]

        #NOTE(bcwaldon): This header is deprecated in favor of X-Auth-Token
        deprecated_token = req.headers.get('X-Storage-Token')

        # FIXME REMOVE 
        service_catalog = None
        if req.headers.get('X-Service-Catalog') is not None:
            try:
                catalog_header = req.headers.get('X-Service-Catalog')
                service_catalog = json.loads(catalog_header)
                print 'service_catalog, PLEASE REMOVE:', service_catalog
            except ValueError:
                raise webob.exc.HTTPInternalServerError(
                        'Invalid service catalog json.')

        kwargs = {
            'auth_token': req.headers.get('X-Auth-Token', deprecated_token),
            'user': req.headers.get('X-User-Id'),
            'tenant': req.headers.get('X-Tenant-Id'),
            'is_admin': CONF.admin_role.strip().lower() in roles,
        }

        return openstack.common.context.RequestContext(**kwargs)


class UnauthenticatedContextMiddleware(BaseContextMiddleware):

    def process_request(self, req):
        req.context = _get_anonymous_context()
