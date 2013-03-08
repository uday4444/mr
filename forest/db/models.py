# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime, Text, )

from oslo.config import cfg
from openstack.common.db.sqlalchemy import types, models

CONF = cfg.CONF
BASE = declarative_base()


class ForestBase(models.SoftDeleteMixin, models.ModelBase):
    pass


class TenantId(BASE, ForestBase):
    ''' Create for each user Project '''
    __tablename__ = 'tenant_id'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    tenant_id = Column(String(255))
    user_id = Column(String(255))


class Workflows(BASE, ForestBase):
    '''
    Represents a Hadoop workflow
    - Master instance assigns Hadoop tasks to cor and task nodes and
      monitors their status.
    - Core instances run Hadoop tasks and store data using the Hadoop
      Distributed File System(HDFS).
    - Task instances run Hadoop tasks, but do not persist data,.
    '''

    __tablename__ = 'workflows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255))

    display_name = Column(String(255))
    display_description = Column(String(255))
    state = Column(Integer)

    master_node_id = Column(Integer)  # reservation id
    master_node_flavor_id = Column(String(255))  # flavor id

    core_node_id = Column(Integer)  # reservation id
    core_node_count = Column(Integer)  # number of instances
    core_nodes_flavor_id = Column(String(255))  # flavor id

    task_node_id = Column(Integer)  # reservation id
    task_node_count = Column(Integer)  # number of instances
    task_node_flavor_id = Column(String(255))  # flavor id

    scheduled_at = Column(DateTime)
    launched_at = Column(DateTime)
    terminated_at = Column(DateTime)

    access_ipaddress = Column(types.IPAddress())

    nodes_info = Column(Text) # TODO: storing json object
