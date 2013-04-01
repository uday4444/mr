# -*- coding: utf-8 -*-

'''
Routines for configuring Forest
'''

import os

from oslo.config import cfg

from openstack.common.pastedeploy import paste_deploy_app
from openstack.common.db.sqlalchemy import session as db_session
from openstack.common import log as logging
from openstack.common import rpc

from forest import paths


__all__ = ('paste_deploy_app',
           'parse_api_config',
           'parse_service_config',
           'parse_config',)


DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('$sqlite_db')
LOG = logging.getLogger(__name__)
CONF = cfg.CONF


paste_deploy_group = cfg.OptGroup('paste_deploy')
paste_deploy_opts = [
    cfg.StrOpt('flavor'),
    cfg.StrOpt('config_file')
]


api_opts = [
    cfg.StrOpt('forest_api_listen',
               default='0.0.0.0',
               help='IP address for OpenStack API to listen'),
    cfg.IntOpt('forest_api_listen_port',
               default=9310,
               help='port for forest api to listen'),
    cfg.IntOpt('forest_api_workers',
               default=None,
               help='Number of workers for forest API service')
]

service_opts = [
    cfg.IntOpt('report_interval',
               default=10,
               help='seconds between nodes reporting state to datastore'),
    cfg.IntOpt('periodic_interval',
               default=60,
               help='seconds between running periodic tasks'),
]


def parse_config(argv, default_config_files=None):
    db_session.set_defaults(sql_connection=DEFAULT_SQL_CONNECTION,
                            sqlite_db='nova.sqlite')
    rpc.set_defaults(control_exchange='nova')
    CONF(argv[1:],
         project='nova',
         default_config_files=default_config_files)


def parse_api_config(argv, default_config_files):
    CONF.register_opts(api_opts)
    parse_config(argv, default_config_files)


def parse_service_config(argv, default_config_files):
    CONF.register_opts(service_opts)
    parse_config(argv, default_config_files)


def _register_paste_deploy_opts():
    ''' Idempotent registration of paste_deploy option group '''
    CONF.register_group(paste_deploy_group)
    CONF.register_opts(paste_deploy_opts, group=paste_deploy_group)


def _get_deployment_flavor():
    '''
    Retrieve the paste_deploy.flavor config item, formatted appropriately
    for appending to the application name.
    '''
    flavor = CONF.paste_deploy.flavor
    return '' if not flavor else ('-' + flavor)


def _get_deployment_config_file():
    '''
    Retrieve the deployment_config_file config item, formatted as an
    absolute pathname.
    '''
    config_file = CONF.paste_deploy.config_file
    if not config_file:
        if CONF.config_file:
            # Assume paste config is in a paste.ini file corresponding
            # to the last config file
            path = os.path.splitext(CONF.config_file[-1])[0] + "-paste.ini"
        else:
            return None
    else:
        path = config_file
    return os.path.abspath(path)


def load_paste_app(app_name=None):
    '''
    Builds and returns a WSGI app from a paste config file.

    We assume the last config file specified in the supplied ConfigOpts
    object is the paste config file.

    :param app_name: name of the application to load
    :raises RuntimeError when config file cannot be located or application
            cannot be loaded from config file
    '''
    if app_name is None:
        app_name = CONF.prog

    # append the deployment flavor to the application name,
    # in order to identify the appropriate paste pipeline
    _register_paste_deploy_opts()
    app_name += _get_deployment_flavor()
    conf_file = _get_deployment_config_file()

    try:
        LOG.debug('Loading %(app_name)s from %(conf_file)s',
                  {'conf_file': conf_file, 'app_name': app_name})

        app = paste_deploy_app(conf_file, app_name, CONF)

        # Log the options used when starting if we're in debug mode...
        if CONF.debug:
            CONF.log_opt_values(LOG, logging.DEBUG)
        return app

    except (LookupError, ImportError) as e:
        msg = ('Unable to load %(app_name)s from '
               'configuration file %(conf_file)s.'
               '\nGot: %(e)r') % locals()
        LOG.error(msg)
        raise RuntimeError(msg)


if __name__ == '__main__':
    import sys
    parse_api_config(sys.argv, None)
    CONF(None, project='forest', prog='test')
    print CONF.forest_api_listen_port
    print CONF.prog
    print CONF.sql_connection
