# -*- coding: utf-8 -*-

import routes

from openstack.common import wsgi
from forest.api.v1 import jobflows


class API(wsgi.Router):
    ''' WSGI router for Forest v1 API requests. '''

    def __init__(self, conf, **local_conf):

        mapper = routes.Mapper()

        # Resource
        jobflows_resource = jobflows.create_resource(conf)
        mapper.resource('jobflow', 'jobflows', controller=jobflows_resource)

        super(API, self).__init__(mapper)
