# -*- coding: utf-8 -*-

from openstack.common import wsgi


class Controller(object):

    def __init__(self):
        pass

    def index(self, req, **kwargs):
        return {'jobflows': [{'I':'x',}, {'I':'e',}, {'I':'o',}]}

    def create(self, req):
        pass


def create_resource():
    ''' Stacks resource factory method '''
    return wsgi.Resource(Controller())
