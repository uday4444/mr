# -*- coding: utf-8 -*-

from openstack.common import wsgi

class Controller(object):

    def __init__(self):
        pass

    def index(self, req):
        return {'name': 'index'}


def create_resource():
    '''
    Stacks resource factory method
    '''
    return wsgi.Resource(Controller())
