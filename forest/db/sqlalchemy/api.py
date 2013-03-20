# -*- coding: utf-8 -*-

from sqlalchemy import or_
from sqlalchemy.orm.session import Session

from openstack.common.db.sqlalchemy.session import get_session
from openstack.common.exception import NotFound

from forest.db.sqlclchemy import models
from forest.common import crypt


def model_query(context, model, *args, **kwargs):
    session = _session(context)
    read_deleted = kwargs.get('read_deleted', context.read_deleted)
    tenant_only = kwargs.get('project_only', False)

    def is_subclass_of_softdeletemixin(obj):
        return (isinstance(obj, type)
                and issubclass(obj, models.SoftDeleteMixin_))

    query = session.query(model, *args)
    base_model = kwargs.get('base_model', model)

    # handle delete action, model must is subclass of SoftDeleteMixin
    if is_subclass_of_softdeletemixin(base_model):

        default_deleted_value = base_model.__mapper__.c.deleted.default.arg
        if read_deleted == 'no':
            query.query.filter(base_model.deleted == default_deleted_value)
            pass
        elif read_deleted == 'yes':
            pass
        elif read_deleted == 'only':
            query.query.filter(base_model.deleted != default_deleted_value)
        else:
            raise Exception('Unrecognized read_deleted value %s'
                             % read_deleted)

    if tenant_only: # FIXME check admin role
        if tenant_only== 'allow_none':
            query = query.filter(or_(base_model.tenant_id == context.tenant_id,
                                     base_model.tenant_id == None))
        else:
            query = query.filter(base_model.tenant_id == context.tenant_id)

    return query


def _session(context):
    return (context and context.session) or get_session()


def job_workflow_get(context, job_workflow_id):
    '''
    If is_admin flag is False, 
    we only allow retrieval of a specific stack in the tenant scoping
    '''
    result = model_query(context, models.JobWorkflow).get(job_workflow_id)

    if (result is not None and context is not None and
            result.tenant_id != context.tenant_id):
        return None

    return result


def job_workflow_get_all(context, tenant_only=True):
    results = (model_query(context, models.JobWorkflow,
                           read_deleted='no', tenant_only=tenant_only)
               .filter_by(owner_id=None).all())
    return results


def job_workflow_get_all_by_tenant(context):
    results = (model_query(context, models.JobWorkflow, read_deleted='no')
               .filter_by(owner_id=None)
               .filter_by(tenant_id=context.tenant_id).all())
    return results


def job_workflow_create(context, values):
    job_workflow_ref = models.JobWorkflow()
    job_workflow_ref.update(values)
    job_workflow_ref.save(_session(context))
    return job_workflow_ref


def job_workflow_update(context, job_workflow_id, values):
    job_workflow = job_workflow_get(context, job_workflow_id)
    if not job_workflow:
        raise NotFound('Attempt to update a job workflow with id: %s '
                       'that does not exist' % job_workflow_id)

    job_workflow.update(values)
    job_workflow.save(_session(context))


def job_workflow_delete(context, job_workflow_id):
    job_workflow = job_workflow_get(context, job_workflow_id)
    if not job_workflow:
        raise NotFound('Attempt to update a job workflow with id: %s '
                       'that does not exist' % job_workflow_id)

    # get object session
    session = Session.object_session(job_workflow)
    session.delete(job_workflow.user_creds) # FIXME Maybe we do not need it
    job_workflow.soft_delete()
    session.flush()

#
# FIXME Maybe we need a ** Super User ** instread save user creds
#

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
