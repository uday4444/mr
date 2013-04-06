# -*- coding: utf-8 -*-

import eventlet
from oslo.config import cfg
from openstack.common import log as logging

LOG = logging.getLogger(__name__)

from novaclient.v1_1 import client as nova_client
from keystoneclient.v2_0 import client as keystone_client

try:
    from swiftclient import client as swift_client
except ImportError:
    swiftclient = None
    LOG.info('swiftclient not available')
try:
    from quantumclient.v2_0 import client as quantum_client
except ImportError:
    quantumclient = None
    LOG.info('quantumclient not available')

from forest.common import exception



class KeystoneClient(object):
    """
    Wrap keystone client so we can encapsulate logic used in resources
    Note this is intended to be initialized from a resource on a per-session
    basis, so the session context is passed in on initialization
    Also note that a copy of this is created every resource as self.keystone()
    via the code in engine/client.py, so there should not be any need to
    directly instantiate instances of this class inside resources themselves
    """
    def __init__(self, context):
        self.context = context
        kwargs = {
            'auth_url': context.auth_url,
        }

        if context.password is not None:
            kwargs['username'] = context.username
            kwargs['password'] = context.password
            kwargs['tenant_name'] = context.tenant
            kwargs['tenant_id'] = context.tenant_id
        elif context.auth_token is not None:
            kwargs['tenant_name'] = context.tenant
            kwargs['token'] = context.auth_token
        else:
            LOG.error("Keystone connection failed, no password or " +
                         "auth_token!")
            return
        self.client = kc.Client(**kwargs)
        self.client.authenticate()

    def create_stack_user(self, username, password=''):
        """
        Create a user defined as part of a stack, either via template
        or created internally by a resource.  This user will be added to
        the heat_stack_user_role as defined in the config
        Returns the keystone ID of the resulting user
        """
        user = self.client.users.create(username,
                                        password,
                                        '%s@heat-api.org' %
                                        username,
                                        tenant_id=self.context.tenant_id,
                                        enabled=True)

        # We add the new user to a special keystone role
        # This role is designed to allow easier differentiation of the
        # heat-generated "stack users" which will generally have credentials
        # deployed on an instance (hence are implicitly untrusted)
        roles = self.client.roles.list()
        stack_user_role = [r.id for r in roles
                           if r.name == cfg.CONF.heat_stack_user_role]
        if len(stack_user_role) == 1:
            role_id = stack_user_role[0]
            LOG.debug("Adding user %s to role %s" % (user.id, role_id))
            self.client.roles.add_user_role(user.id, role_id,
                                            self.context.tenant_id)
        else:
            LOG.error("Failed to add user %s to role %s, check role exists!"
                         % (username,
                            cfg.CONF.heat_stack_user_role))

        return user.id

    def delete_stack_user(self, user_id):

        user = self.client.users.get(user_id)

        # FIXME (shardy) : need to test, do we still need this retry logic?
        # Copied from user.py, but seems like something we really shouldn't
        # need to do, no bug reference in the original comment (below)...
        # tempory hack to work around an openstack bug.
        # seems you can't delete a user first time - you have to try
        # a couple of times - go figure!
        tmo = eventlet.Timeout(10)
        status = 'WAITING'
        reason = 'Timed out trying to delete user'
        try:
            while status == 'WAITING':
                try:
                    user.delete()
                    status = 'DELETED'
                except Exception as ce:
                    reason = str(ce)
                    LOG.warning("Problem deleting user %s: %s" %
                                   (user_id, reason))
                    eventlet.sleep(1)
        except eventlet.Timeout as t:
            if t is not tmo:
                # not my timeout
                raise
            else:
                status = 'TIMEDOUT'
        finally:
            tmo.cancel()

        if status != 'DELETED':
            raise exception.Error(reason)

    def delete_ec2_keypair(self, user_id, accesskey):
        self.client.ec2.delete(user_id, accesskey)

    def get_ec2_keypair(self, user_id):
        # We make the assumption that each user will only have one
        # ec2 keypair, it's not clear if AWS allow multiple AccessKey resources
        # to be associated with a single User resource, but for simplicity
        # we assume that here for now
        cred = self.client.ec2.list(user_id)
        if len(cred) == 0:
            return self.client.ec2.create(user_id, self.context.tenant_id)
        if len(cred) == 1:
            return cred[0]
        else:
            LOG.error("Unexpected number of ec2 credentials %s for %s" %
                         (len(cred), user_id))


class Clients(object):
    '''
    Convenience class to create and cache client instances.
    '''

    def __init__(self, context):
        self.context = context
        self._nova = {}
        self._keystone = None
        self._swift = None  # Object store API
        self._quantum = None  # Network API

    def keystone(self):
        if self._keystone:
            return self._keystone

        self._keystone = KeystoneClient(self.context)
        return self._keystone

    def nova(self, service_type='compute'):
        if service_type in self._nova:
            return self._nova[service_type]

        con = self.context
        args = {
            'project_id': con.tenant,
            'auth_url': con.auth_url,
            'service_type': service_type,
        }

        if con.password is not None:
            args['username'] = con.username
            args['api_key'] = con.password
        elif con.auth_token is not None:
            args['username'] = con.service_user
            args['api_key'] = con.service_password
            args['project_id'] = con.service_tenant
            args['proxy_token'] = con.auth_token
            args['proxy_tenant_id'] = con.tenant_id
        else:
            LOG.error("Nova connection failed, no password or auth_token!")
            return None

        client = None
        try:
            # Workaround for issues with python-keyring, need no_cache=True
            # ref https://bugs.launchpad.net/python-novaclient/+bug/1020238
            # TODO(shardy): May be able to remove when the bug above is fixed
            client = nova_client.Client(1.1, no_cache=True, **args)
            client.authenticate()
            self._nova[service_type] = client
        except TypeError:
            # for compatibility with essex, which doesn't have no_cache=True
            # TODO(shardy): remove when we no longer support essex
            client = nova_client.Client(1.1, **args)
            client.authenticate()
            self._nova[service_type] = client

        return client

    def swift(self):
        if swiftclient is None:
            return None
        if self._swift:
            return self._swift

        con = self.context
        args = {
            'auth_version': '2'
        }

        if con.password is not None:
            args['user'] = con.username
            args['key'] = con.password
            args['authurl'] = con.auth_url
            args['tenant_name'] = con.tenant
        elif con.auth_token is not None:
            args['user'] = None
            args['key'] = None
            args['authurl'] = None
            args['preauthtoken'] = con.auth_token
            # Lookup endpoint for object-store service type
            service_type = 'object-store'
            endpoints = self.keystone().service_catalog.get_endpoints(
                service_type=service_type)
            if len(endpoints[service_type]) == 1:
                args['preauthurl'] = endpoints[service_type][0]['publicURL']
            else:
                LOG.error("No endpoint found for %s service type" %
                             service_type)
                return None
        else:
            LOG.error("Swift connection failed, no password or " +
                         "auth_token!")
            return None

        self._swift = swiftclient.Connection(**args)
        return self._swift

    def quantum(self):
        if quantum_client is None:
            return None
        if self._quantum:
            LOG.debug('using existing _quantum')
            return self._quantum

        con = self.context
        args = {
            'auth_url': con.auth_url,
            'service_type': 'network',
        }

        if con.password is not None:
            args['username'] = con.username
            args['password'] = con.password
            args['tenant_name'] = con.tenant
        elif con.auth_token is not None:
            args['username'] = con.service_user
            args['password'] = con.service_password
            args['tenant_name'] = con.service_tenant
            args['token'] = con.auth_token
        else:
            LOG.error("Quantum connection failed, "
                         "no password or auth_token!")
            return None
        LOG.debug('quantum args %s', args)

        self._quantum = quantum_client.Client(**args)

        return self._quantum
