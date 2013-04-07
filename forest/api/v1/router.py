# -*- coding: utf-8 -*-

import routes

from openstack.common import wsgi
from forest.api.v1 import workflows


class API(wsgi.Router):
    ''' WSGI router for Forest v1 API requests. '''

    def __init__(self, conf, **local_conf):
        self.conf = conf
        mapper = routes.Mapper()
        # Resource
        workflows_resource = workflows.create_resource() # FIXME
        mapper.connect('/', controller=workflows_resource, action='index')

        super(API, self).__init__(mapper)
