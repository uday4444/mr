# -*- coding: utf-8 -*-

from novaclient.v1_1 import client;
from novaclient import exceptions as novaexceptions

username = "admin";
password = "openstack";
tenant = "admin"
authurl = "http://192.168.10.70:5000/v2.0/"

#  export OS_TENANT_NAME=admin
#  export OS_USERNAME=admin
#  export OS_PASSWORD=openstack
#  export OS_AUTH_STRATEGY=keystone
#  export SERVICE_TOKEN=bdbb8df712625fa7d1e0ff1e049e8aab
#  export SERVICE_ENDPOINT=http://192.168.10.70:35357/v2.0/

#create the client object
osconn = client.Client(username, password, tenant, authurl);

#Query OpenStack installation
print osconn.servers.list()
print osconn.flavors.list()
print osconn.keypairs.list()
print osconn.images.list()

q = osconn.quotas.get(username)
print q._info.keys()
