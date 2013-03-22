# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import Session
from sqlalchemy import (Column, Integer, String, DateTime, Text, ForeignKey)

from openstack.commom import uuidutils, timeutils
from openstack.common.db.sqlalchemy import types, models
from openstack.common.db.sqlalchemy.session import get_session

from oslo.config import cfg


CONF = cfg.CONF
BASE = declarative_base()


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


class JobWorkflow(BASE, ForestBase, models.SoftDeleteMixin):
    '''
    Represents a Hadoop workflow
    - Master instance assigns Hadoop tasks to cor and task nodes and
      monitors their status.
    - Core instances run Hadoop tasks and store data using the Hadoop
      Distributed File System(HDFS).
    - Task instances run Hadoop tasks, but do not persist data,.
    '''

    __tablename__ = 'job_workflows'

    id = Column(String, primary_key=True, default=uuidutils.generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(String(255))

    owner_id = Column(String(255), nullable=False)
    tenant_id = Column(String(255))

    # Hadoop cluster info
    access_ipaddress = Column(types.IPAddress())

    state = Column(Integer)  # FIXME default value
    scheduled_at = Column(DateTime)
    launched_at = Column(DateTime)
    terminated_at = Column(DateTime)
    # - - - - - -
    master_node_id = Column(Integer)  # reservation id
    master_node_flavor_id = Column(String(255))  # flavor id
    # - - - - - -
    core_node_id = Column(Integer)  # reservation id
    core_node_count = Column(Integer)  # number of instances
    core_nodes_flavor_id = Column(String(255))  # flavor id
    # - - - - - -
    task_node_id = Column(Integer)  # reservation id
    task_node_count = Column(Integer)  # number of instances
    task_node_flavor_id = Column(String(255))  # flavor id

    user_creds_id = Column(
        Integer,
        ForeignKey('user_creds.id'),
        nullable=False)

    nodes_info = Column(Text)  # TODO: storing json object ?


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
    job_workflow = relationship(JobWorkflow, backref=backref('user_creds'))
