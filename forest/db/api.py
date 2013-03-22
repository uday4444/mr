# -*- coding: utf-8 -*-
''' Interface for database access '''

from oslo.config import cfg
from openstack.common.db import api as db_api
from openstack.common import log as logging

# from forest import utils


CONF = cfg.CONF

_BACKEND_MAPPING = {'sqlalchemy': 'forest.db.sqlclchemy.api'}

IMPL = db_api.DBAPI(backend_mapping=_BACKEND_MAPPING)
LOG = logging.getLogger(__name__)


def get_session(context=None):
    ''' Get session from context '''
    return IMPL.get_session(context)


def job_workflow_get(context, job_workflow_id):
    return IMPL.job_workflow_get(context, job_workflow_id)


def job_workflow_get_all(context, tenant_only=True):
    return IMPL.job_workflow_get_all(context, tenant_only)


def job_workflow_get_all_by_tenant(context):
    return IMPL.job_workflow_get_all_by_tenant(context)


def job_workflow_create(context, values):
    return job_workflow_create(context, values)


def job_workflow_update(context, job_workflow_id, values):
    job_workflow_update(context, job_workflow_id, values)


def job_workflow_delete(context, job_workflow_id):
    job_workflow_delete(context, job_workflow_id)


# - - - - - - - - - - - - - - - - - - - #


def user_creds_create(context):
    return IMPL.user_creds_create(context)


def user_creds_get(user_creds_id):
    return IMPL.user_creds_get(user_creds_id)
