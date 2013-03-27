# -*- coding: utf-8 -*-

import sys

from openstack.common import log as logging
from openstack.common.db.sqlalchemy.session import get_engine

from forest import config
from forest.db.sqlalchemy.models import BASE
from forest.scripts.cli import prompt_bool


def config_for_engine(argv):
    config.parse_args(argv)
    logging.setup('forest')
    engine = get_engine()
    return engine


def init_db(argv=sys.argv):
    engine = config_for_engine(argv)
    BASE.metadata.create_all(engine)


def drop_db(argv=sys.argv):
    engine = config_for_engine(argv)
    select = True if (len(argv) == 3 and argv[2] == 'Y') else False

    if select or prompt_bool("Are you sure you want to lose all your data"):
        BASE.metadata.drop_all(engine)


if __name__ == '__main__':
    init_db()
    drop_db()
