'''
A filter middleware that inspects the requested URI for a version string
and/or Accept headers and attempts to negotiate an API controller to
return
'''

from oslo.config import cfg

import openstack.common.log as logging
import openstack.common.wsgi

from forest.api import versions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class VersionNegotiationFilter(openstack.common.wsgi.Middleware):

    def __init__(self, app, global_conf, **local_conf):
        self.versions_app = versions.Controller()
        super(VersionNegotiationFilter, self).__init__(app)

    def process_request(self, req):
        ''' Try to find a version first in the accept header, then the URL '''
        msg = ("Determining version of request: %(method)s %(path)s"
               " Accept: %(accept)s")
        args = {'method': req.method, 'path': req.path, 'accept': req.accept}
        LOG.debug(msg % args)

        if req.path_info_peek() == "versions":
            return self.versions_app

        try:
            # Remove version in url so it doesn't conflict later
            req_version = req.path_info_pop()

            # does not fix it
            # req.path_info = ''.join(('/v', str(version), req.path_info))
            if req.path_info == '':
                return self.versions_app

            req.path_info = req.path_info
            version = self._match_version_string(req_version)
            req.environ['api.version'] = version

            LOG.debug("Matched version: v%d", version)
            LOG.debug('new uri %s' % req.path_info)
            return None
        except ValueError:
            LOG.debug("Unknown version. Returning version choices.")
            return self.versions_app


    def _match_version_string(self, subject):
        '''
        Given a string, tries to match a major and/or
        minor version number.

        :param subject: The string to check
        :returns version found in the subject
        :raises ValueError if no acceptable version could be found
        '''
        if subject in ('v1', 'v1.0'):
            major_version = 1
        else:
            raise ValueError()
        return major_version
