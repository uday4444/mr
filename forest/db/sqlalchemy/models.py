# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import Session
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        Enum, Boolean)

from openstack.commom import uuidutils, timeutils
from openstack.common.db.sqlalchemy import types, models
from openstack.common.db.sqlalchemy.session import get_session

from oslo.config import cfg


CONF = cfg.CONF
BASE = declarative_base()

DEFAULT_DELETED_VALUE = models.SoftDeleteMixin.deleted.default.arg


class ForestBase(models.ModelBase):
    '''
    models.ModelBase contains created_at and updated_at (auto update)
    '''

    def _get_session(self):
        session = Session.object_session(self)
        if not session:
            session = get_session()
        return session

    def save(self, session=None):
        ''' Save this object. '''
        if not session:
            session = self._get_session()

        # NOTE(boris-42): This part of code should be look like:
        #                       sesssion.add(self)
        #                       session.flush()
        #                 But there is a bug in sqlalchemy and eventlet that
        #                 raises NoneType exception if there is no running
        #                 transaction and rollback is called. As long as
        #                 sqlalchemy has this bug we have to create transaction
        #                 explicity.
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def expire(self, session, attrs=None):
        ''' Refresh this object. '''
        if not session:
            session = self._get_session()
        session.expire(self, attrs)

    def delete(self, session=None):
        ''' Delete this object '''
        self.deleted = True
        self.deleted_at = timeutils.utcnow()

        if not session:
            session = self._get_session()

        session.delete(self)
        session.flush()

    def refresh(self, session=None, attrs=None):
        if not session:
            session = self._get_session()
        session.refresh(self, attrs)


def convert_datetimes(values, *datetime_keys):
    for key in values:
        if key in datetime_keys and isinstance(values[key], basestring):
            values[key] = timeutils.parse_strtime(values[key])
    return values


class JobFlow(BASE, ForestBase, models.SoftDeleteMixin):
    '''
    Represents a Hadoop kflow
    - Master instance assigns Hadoop tasks to cor and task nodes and
      monitors their status.
    - Core instances run Hadoop tasks and store data using the Hadoop
      Distributed File System(HDFS).
    - Task instances run Hadoop tasks, but do not persist data,.

    Not supported now:
    - bootstrap action
    - loguri
    - last_state_change_reason
    - jobflow role / ami
    '''

    __tablename__ = 'job_flows'

    id = Column(String, primary_key=True, default=uuidutils.generate_uuid)
    name = Column(String(255), nullable=False)

    owner_id = Column(String(255), nullable=False)
    tenant_id = Column(String(255))

    # details
    key_name = Column(String(255))
    subnet_id = Column(String(255))
    region_name = Column(String(255))
    termination_protected = Column(Boolean, default=False)
    access_ipaddress = Column(types.IPAddress())  #TODO DNSName is better

    instance_groups = relationship('InstanceGroup',
                                   primaryjoin='and_(JobFlow.id =='
                                       'InstanceGroup.job_flow_id, '
                                       'InstanceGroup.deleted =='
                                       '%d' % DEFAULT_DELETED_VALUE)

    # job flow execution status detail
    created_at = Column(DateTime)
    ended_at = Column(DateTime)
    ready_at = Column(DateTime)
    started_at = Column(DateTime)
    last_state_change_reason = Column(String)
    state = Column(Enum('COMPLETED', 'FAILED', 'TERMINATED', 'RUNNING',
                        'SHUTTING_DOWN', 'STARTING', 'WAITING',
                        'BOOTSTRAPPING'))

    user_creds_id = Column(Integer, ForeignKey('user_creds.id'),
                           nullable=False)


class InstanceGroup(BASE, ForestBase, models.SoftDeleteMixin):

    __tablename__ = 'instance_groups'

    id = Column(String, primary_key=True, default=uuidutils.generate_uuid)
    name = Column(String(255), nullable=False)  #Friendly name given to the instance group

    request_count = Column(Integer, nullable=False)
    running_count = Column(Integer, default=0)
    type = Column(String(255))
    role = Column(Enum('MASTER', 'CORE', 'TASK'))

    created_at = Column(DateTime)
    terminated_at = Column(DateTime)
    started_at = Column(DateTime)
    ready_at = Column(DateTime)
    last_state_change_reason = Column(String)
    state = Column(Enum('PROVISIONING', 'BOOTSTRAPPING', 'RUNNING',
                        'RESIZING', 'ARRESTED', 'SHUTTING_DOWN', 'ENDED'))

    job_flow_id = Column(String, ForeignKey('job_flows.id'))


# TODO: Whether it is the only appropriate way
class UserCreds(BASE, ForestBase):
    '''
    Represents user credentials and mirrors the 'context'
    handed in by wsgi.
    '''

    _tablename__ = 'user_creds'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    service_user = Column(String)
    service_password = Column(String)
    tenant = Column(String)
    auth_url = Column(String)
    aws_auth_url = Column(String)
    tenant_id = Column(String)
    aws_creds = Column(String)
    job_flow = relationship(JobFlow, backref=backref('user_creds'))
