# -*- coding: utf-8 -*-


import routes
import openstack.common.wsgi


class Router(openstack.common.wsgi.Router):
    @classmethod
    def factory(cls, global_conf, **local_conf):
        mapper = routes.Mapper()
        return cls(mapper)


class Middleware(openstack.common.wsgi.Middleware):
    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(app)
        return filter
