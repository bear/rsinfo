#!/usr/bin/env python
#
# :copyright: (c) 2013 by Mike Taylor
# :author:    Mike Taylor
# :license:   BSD 2-Clause
#
#  See LICENSE file for details
#

import os
import time
import json
import argparse

import pyrax


_data_centers = [ 'DFW', 'ORD' ]
_commands     = [ 'list' ]
_config_file  = '~/.rackspace.cfg'
_username     = 'ops'
_marker       = '##### auto-generated for rsinfo #####'

_usage = """
  list    list details for the servers
            If a server name is specified, the list will
            only contain that server
            If a datacenter has been given, the list will only
            contain those servers
  hosts   generate output that can be used in /etc/hosts
  ssh     generate output that can be used in ~/.ssh/config

  Config File Format:
      [rackspace_cloud]
      username = USERNAME
      api_key = KEY
"""

def loadConfig():
    parser = argparse.ArgumentParser(epilog=_usage, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-c', '--config',     default=_config_file, help='where to retrieve configuration items and the rackspace API keys (default: %(default)s)')
    parser.add_argument('-d', '--datacenter', default='ALL',        help='datacenter to work within (default: %(default)s)', choices=_data_centers)
    parser.add_argument('-s', '--server',                           help='limit output to the named server')

    parser.add_argument('command', choices=['list', 'hosts', 'ssh'])

    return parser.parse_args()

def initCredentials(datacenter):
    pyrax.set_setting("identity_type", "rackspace")
    pyrax.set_credential_file(os.path.expanduser(cfg.config), datacenter)

def loadServers(datacenters):
    # {'OS-EXT-STS:task_state': None, 
    #  'addresses': { u'public': [], 
    #                 u'private': []
    #               }, 
    #  'links': [],
    #  'image': { u'id': u'GUID', 
    #             u'links': []
    #           }, 
    #  'manager': <novaclient.v1_1.servers.ServerManager object at 0x101abb450>, 
    #  'OS-EXT-STS:vm_state': u'active', 
    #  'flavor': { u'id': u'2', 
    #              u'links': []
    #            }, 
    #  'id': u'', 
    #  'user_id': u'NNN', 
    #  'OS-DCF:diskConfig': u'AUTO', 
    #  'accessIPv4': u'', 
    #  'accessIPv6': u'', 
    #  'progress': 100, 
    #  'OS-EXT-STS:power_state': 1, 
    #  'metadata': {}, 
    #  'status': u'ACTIVE', 
    #  'updated': u'2013-04-25T05:11:09Z', 
    #  'hostId': u'', 
    #  'key_name': None, 
    #  'name': u'sssss', 
    #  'created': u'2013-02-11T19:33:31Z', 
    #  'tenant_id': u'NNN', 
    #  '_info': {}, 
    #  'config_drive': u'', 
    #  '_loaded': True
    # }
    result = {}
    for dc in datacenters:
        initCredentials(dc)

        cs = pyrax.cloudservers
        for s in cs.servers.list(detailed=True):
            if s.name not in result:
                result[s.name] = None
            result[s.name] = s
    return result

def getServerInfo(serverName, serverList):
    result = None

    if cfg.datacenter == 'ALL':
        s = ' in server list'
    else:
        s = ' in datacenter %s' % cfg.datacenter

    if serverName not in serverList:
        print '%s not found %s' % (serverName, s)
    else:
        item   = serverList[serverName]
        result = {}
        for key in ( 'accessIPv4', 'status', 'name' ):
            result[key] = item.__getattr__(key)

    return result

_hosts_config = """%(accessIPv4)s\t%(name)s\n"""

def generateHostsFile(servers):
    hosts = []

    f = False
    for line in open('/etc/hosts', 'r').readlines():
        if line.startswith(_marker):
            f = not f
        else:
            if not f:
                hosts.append(line)

    hosts.append('\n%s\n' % _marker)

    for s in servers:
        r = getServerInfo(s, servers)
        hosts.append(_hosts_config % r)

    hosts.append('\n%s\n' % _marker)

    open('/tmp/_hosts_', 'w+').write(''.join(hosts))

_ssh_config = """Host %(name)s
User %(username)s
StrictHostKeyChecking no
IdentityFile ~/.ssh/id_rsa

"""

def generateConfigFile(servers):
    hosts = []

    f = False
    for line in open(os.path.expanduser('~/.ssh/config'), 'r').readlines():
        if line.startswith(_marker):
            f = not f
        else:
            if not f:
                hosts.append(line)

    hosts.append('\n%s\n' % _marker)

    for s in servers:
        r = getServerInfo(s, servers)
        r['username'] = _username
        hosts.append(_ssh_config % r)

    hosts.append('\n%s\n' % _marker)

    open('/tmp/_ssh_config_', 'w+').write(''.join(hosts))

def getCommandParam(cmdText, commands):
    try:
        p      = commands.index(cmdText)
        result = commands[p + 1]
    except:
        result = ''
    return result

if __name__ == '__main__':
    cfg = loadConfig()

    if cfg.datacenter == 'ALL':
        datacenters = _data_centers
    else:
        datacenters = [ datacenter ]

    servers = loadServers(datacenters)

    if cfg.command == 'list':
        results = []

        if cfg.server is None:
            for s in servers:
                r = getServerInfo(s, servers)
                if r is not None:
                    results.append(r)
        else:
            r = getServerInfo(cfg.server, servers)
            if r is not None:
                results.append(r)

        print json.dumps(results)

    elif cfg.command == 'hosts':
        generateHostsFile(servers)
    elif cfg.command == 'ssh':
        generateConfigFile(servers)
