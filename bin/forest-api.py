#co
"""
Forest API Server. An OpenStack ReST API to Forest.
"""


from heat.common import config
from heat.common import wsgi


if __name__ == '__main__':
    try:
        cfg.CONF(project='heat', prog='heat-api')
        cfg.CONF.default_log_levels = ['amqplib=WARN',
                                       'qpid.messaging=INFO',
                                       'keystone=INFO',
                                       'eventlet.wsgi.server=WARN',
                                       ]
        logging.setup('heat')

        app = config.load_paste_app()

        port = cfg.CONF.bind_port
        host = cfg.CONF.bind_host
        LOG.info('Starting Heat ReST API on %s:%s' % (host, port))
        server = wsgi.Server()
        server.start(app, cfg.CONF, default_port=port)
        server.wait()
    except RuntimeError, e:
        sys.exit("ERROR: %s" % e)

import eventlet
eventlet.monkey_patch(os=False)

import os
import sys

from oslo.config import cfg

# If ../forest/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "forest", "__init__.py")):
    sys.path.insert(0, possible_topdir)


from openstack.common import log as logging
from openstack.common import service
from openstack.common import wsgi
from forest import config
from forest.common.paste_config import load_paste_app

CONF = cfg.CONF
CONF.import_opt('enabled_apis', 'nova.api')  # FIXME

LOG = logging.getLogger('forest.api')



if __name__ == '__main__':
    config.parse_args(sys.argv)
    logging.setup("nova")

    launcher = service.ProcessLauncher()
    for api_name in CONF.enabled_apis:
        app = load_paste_app(api_name)

        server = wsgi.Server(app, )
        server = service.WSGIService(ap, use_ssl=should_use_ssl)
        launcher.launch_server(server, workers=server.workers or 1)
    launcher.wait()
