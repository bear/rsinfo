rsinfo
======

Rackspace Server Info

Comand-line tool to list, manage and otherwise work with Rackspace Servers.

    usage: rsinfo.py [-h] [-c CONFIG] [-d {DFW,ORD}] [-s SERVER] {list,hosts,ssh}

      -c CONFIG, --config CONFIG
                        where to retrieve configuration items and the
                        rackspace API keys (default: ~/.rackspace.cfg)
  
      -d {DFW,ORD}, --datacenter {DFW,ORD}
                        datacenter to work within (default: ALL)

      -s SERVER, --server SERVER
                        limit output to the named server

      list    list details for the servers
                If a server name is specified, the list will
                only contain that server
                If a datacenter has been given, the list will only
                contain those servers
      hosts   generate output that can be used in /etc/hosts
      ssh     generate output that can be used in ~/.ssh/config

The hosts command will try to generate a new hosts file in place, but if it does not
write priviledges it will write the generated data to /tmp/hosts.new 

The ssh command will try to generate a new config file in place and will fall back to
/tmp/ssh_config.new

The configuration file contains the Rackspace API key and follows their format style

    [rackspace_cloud]
    username = USERNAME
    api_key = KEY


Requirements:
  Python    v2.7+
  pyrax     v1.5+   https://pypi.python.org/pypi/pyrax/
