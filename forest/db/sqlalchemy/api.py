# -*- coding: utf-8 -*-

import sys

from sqlalchemy.orm.session import Session
from sqlalchemy import or_

from openstack.common.db.sqlalchemy.models import SoftDeleteMixin
from openstack.common.db.sqlalchemy.session import get_session
from openstack.common.exception import NotFound

from forest.db.sqlalchemy import models


def get_backend():
    ''' The backend is this module itself. '''
    return sys.modules[__name__]

def _session(context):
    ''' Get session from context '''
    return (context and context.session) or get_session()


def model_query(context, model, *args, **kwargs):
    session = _session(context)
    read_deleted = kwargs.get('read_deleted',
                              getattr(context, 'read_deleted', 'no'))
    tenant_only = kwargs.get('project_only', False)

    def is_subclass_of_softdeletemixin(obj):
        return (isinstance(obj, type)
                and issubclass(obj, SoftDeleteMixin))

    query = session.query(model, *args)
    base_model = kwargs.get('base_model', model)

    # handle delete action, model must is subclass of SoftDeleteMixin
    if is_subclass_of_softdeletemixin(base_model):

        default_deleted_value = base_model.__mapper__.c.deleted.default.arg
        if read_deleted == 'no':
            query = query.filter(base_model.deleted == default_deleted_value)
            pass
        elif read_deleted == 'yes':
            pass
        elif read_deleted == 'only':
            query = query.filter(base_model.deleted != default_deleted_value)
        else:
            raise Exception('Unrecognized read_deleted value %s'
                            % read_deleted)

    if tenant_only:  # FIXME check admin role
        if tenant_only == 'allow_none':
            query = query.filter(or_(base_model.tenant_id == context.tenant_id,
                                     base_model.tenant_id == None))
        else:
            query = query.filter(base_model.tenant_id == context.tenant_id)

    return query


def job_flow_get(context, job_flow_id):
    '''
    If is_admin flag is False,
    we only allow retrieval of a specific stack in the tenant scoping
    '''
    result = (model_query(context, models.JobFlow)
              .filter_by(id=job_flow_id).first())  # TODO joinedload instance group

    if (result is not None and context is not None and
            result.tenant_id != context.tenant_id):
        return None

    return result


def job_flow_get_all(context, tenant_only=True):
    results = (model_query(context, models.JobFlow,
                          read_deleted='no', tenant_only=tenant_only)
               .filter_by(owner_id=None).all())
    return results


def job_flow_get_all_by_tenant(context):
    results = (model_query(context, models.JobFlow, read_deleted='no')
               .filter_by(owner_id=None)
               .filter_by(tenant_id=context.tenant_id).all())
    return results


def job_flow_create(context, values):
    job_flow_ref = models.JobFlow()
    job_flow_ref.update(values)
    job_flow_ref.save(_session(context))
    return job_flow_ref


def job_flow_update(context, job_flow_id, values):
    job_flow_ref = job_flow_get(context, job_flow_id)
    if not job_flow_ref:
        raise NotFound('Attempt to update a job flow with id: %s '
                       'that does not exist' % job_flow_id)

    job_flow_ref.update(values)
    job_flow_ref.save(_session(context))


def job_flow_delete(context, job_flow_id):
    job_flow_ref = job_flow_get(context, job_flow_id)
    if not job_flow_ref:
        raise NotFound('Attempt to update a job flow with id: %s '
                       'that does not exist' % job_flow_id)
    # get object session
    session = Session.object_session(job_flow_ref)

    job_flow_ref.soft_delete()
    count = (session.query(models.InstanceGroup)
             .filter_by(job_flow_id=job_flow_id)
             .soft_delete())
    if count == 0:
        pass  # FIX
    session.delete(job_flow_ref.user_creds)  # FIXME Maybe we do not need it
    session.flush()


def instance_group_create(context, values):
    instance_group_ref = models.InstanceGroup()
    instance_group_ref.update(values)
    instance_group_ref.save(_session(context))
    return instance_group_ref


def instance_group_get(context, instance_group_id):
    result = (model_query(context, models.InstanceGroup)
              .filter_by(id=instance_group_id).first())
    return result


def instance_group_get_by_job_flow(context, job_flow_id):
    result = (model_query(context, models.InstanceGroup)
              .filter_by(job_flow_id=job_flow_id).all())
    return result


def instance_group_update(context, instance_group_id, values):
    instance_group_ref = instance_group_get(context, instance_group_id)
    if not instance_group_ref:
        raise NotFound('Attempt to update a instance group with id: %s '
                       'that does not exist' % instance_group_id)

    instance_group_ref.update(values)
    instance_group_ref.save(_session(context))


def instance_group_delete(context, instance_group_id):
    result = (model_query(context, models.InstanceGroup)
              .filter_by(id=instance_group_id).soft_delete())
    if not result:
        raise NotFound('Attempt to update a instance group with id: %s '
                       'that does not exist' % instance_group_id)

#
# FIXME Maybe we need a ** Super User ** instread of saving user creds
#
from forest.common import crypt  # FIXME


def user_creds_create(context):
    values = context.to_dict()
    user_creds_ref = models.UserCreds()
    user_creds_ref.update(values)
    user_creds_ref.password = crypt.encrypt(values['password'])
    user_creds_ref.service_password = crypt.encrypt(values['service_password'])
    user_creds_ref.aws_creds = crypt.encrypt(values['aws_creds'])
    user_creds_ref.save(_session(context))
    return user_creds_ref


def user_creds_get(user_creds_id):
    db_result = model_query(None, models.UserCreds).get(user_creds_id)
    # return a dict copy of db results, it can be committed back to db
    result = dict(db_result)
    result['password'] = crypt.decrypt(result['password'])
    result['service_password'] = crypt.decrypt(result['service_password'])
    result['aws_creds'] = crypt.decrypt(result['aws_creds'])
    return result
