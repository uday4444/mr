# -*- coding: utf-8 -*-

from openstack.common import wsgi


class Controller(object):

    def __init__(self, conf):
        self.conf = conf

    def index(self, req, **action_args):
        return {'jobflows': [{'I':'x',}, {'I':'e',}, {'I':'o',}]}

    def create(self, req, **action_args):
        raise NotImplementedError()

    def new(self, req, **action_args):
        raise NotImplementedError()

    def update(self, req, **action_args):
        raise NotImplementedError()

    def delete(self, req, **action_args):
        raise NotImplementedError()

    def show(self, req, **action_args):
        raise NotImplementedError()

    def edit(self, req, **action_args):
        self.update(req, **action_args)


def create_resource(conf):
    ''' Stacks resource factory method '''
    return wsgi.Resource(Controller(conf))
