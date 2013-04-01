# -*- coding: utf-8 -*-
import os

from oslo.config import cfg
from openstack.common.pastedeploy import paste_deploy_app
from openstack.common import log as logging

paste_deploy_opts = [
    cfg.StrOpt('flavor'),
    cfg.StrOpt('config_file'),
]

CONF = cfg.CONF
CONF.register_opts(paste_deploy_opts, group='paste_deploy')
LOG = logging.getLogger(__name__)


def _get_deployment_flavor():
    '''
    Retrieve the paste_deploy.flavor config item, formatted appropriately
    for appending to the application name.
    '''
    flavor = CONF.paste_deploy.flavor
    return '' if not flavor else ('-' + flavor)


def _get_paste_config_path():
    paste_suffix = '-paste.ini'
    conf_suffix = '.conf'
    if CONF.config_file:
        # Assume paste config is in a paste.ini file corresponding
        # to the last config file
        path = CONF.config_file[-1].replace(conf_suffix, paste_suffix)
    else:
        path = CONF.prog + '-paste.ini'
    return CONF.find_file(os.path.basename(path))


def _get_deployment_config_file():
    '''
    Retrieve the deployment_config_file config item, formatted as an
    absolute pathname.
    '''
    path = CONF.paste_deploy.config_file
    if not path:
        path = _get_paste_config_path()
    if not path:
        msg = 'Unable to locate paste config file for %s.' % CONF.prog
        raise RuntimeError(msg)
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
