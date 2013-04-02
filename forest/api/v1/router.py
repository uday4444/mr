# -*- coding: utf-8 -*-

from forest.common import wsgi
from forest.api.v1 import workflows


class API(wsgi.Router):
    ''' WSGI router for Forest v1 API requests. '''

    def __init__(self, mapper):
        workflows_resource = workflows.create_resource()
        mapper.connect('/', controller=workflows_resource, action='index')
        super(API, self).__init__(mapper)
