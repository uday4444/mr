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
    return IMPL.job_workflow_create(context, values)


def job_workflow_update(context, job_workflow_id, values):
    IMPL.job_workflow_update(context, job_workflow_id, values)


def job_workflow_delete(context, job_workflow_id):
    IMPL.job_workflow_delete(context, job_workflow_id)


def instance_group_create(context, values):
    return IMPL.instance_group_create(context, values)


def instance_group_get(context, instance_group_id):
    return IMPL.instance_group_get(context, instance_group_id)


def instance_group_get_by_job_flow(context, job_flow_id):
    return IMPL.instance_group_get_by_job_flow(context, job_flow_id)


def instance_group_update(context, instance_group_id, values):
    IMPL.instance_group_update(context, instance_group_id, values)


def instance_group_delete(context, instance_group_id):
    IMPL.instance_group_delete(context, instance_group_id)


# - - - - - - - - - - - - - - - - - - - #


def user_creds_create(context):
    return IMPL.user_creds_create(context)


def user_creds_get(user_creds_id):
    return IMPL.user_creds_get(user_creds_id)
