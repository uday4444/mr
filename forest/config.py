# -*- coding: utf-8 -*-

from oslo.config import cfg
from openstack.common import rpc
from openstack.common.db.sqlalchemy import session as db_session
from forest import paths

__all__ = ('parse_args', )


_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('$sqlite_db')


def parse_args(argv, default_config_files=None):
    # Default sqlite database config #  FIXME
    # FIXME The api is wrong
    cfg.set_defaults(db_session.sql_opts,
                     sql_connection=_DEFAULT_SQL_CONNECTION)
    cfg.set_defaults(db_session.sql_opts, sqlite_db='forest.sqlite')
    # Default rabbitmq control_exchange config
    rpc.set_defaults(control_exchange='forest')
    # Generate the common config
    cfg.CONF(argv[1:],
             project='forest',
             default_config_files=default_config_files)


# TODO Simple test, REMOVE!
if __name__ == '__main__':
    import sys
    #import pprint
    parse_args(sys.argv)
    #pprint.pprint(cfg.CONF.__dict__)
    print ''
    print cfg.CONF.sql_connection
