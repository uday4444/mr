# -*- coding: utf-8 -*-

import httplib
import json
import webob.dec

class Controller(object):
    ''' A controller that produces information on the heat API versions. '''

    @webob.dec.wsgify
    def __call__(self, req):
        ''' Respond to a request for all OpenStack API versions. '''
        version_objs = [{
            'id': 'v1.0',
            'status': 'CURRENT',
            'links': [{
                'rel': 'self',
                'href': self.get_href(req)
            }]
        }]

        response = webob.Response(request=req,
                                  status=httplib.MULTIPLE_CHOICES,
                                  content_type='application/json')
        response.body = json.dumps(dict(versions=version_objs))
        return response

    def get_href(self, req):
        return "%s/v1/" % req.host_url
