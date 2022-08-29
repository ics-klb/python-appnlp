#!/usr/bin/env python

from twisted.web import server, resource, static
from twisted.application import service, internet

from botnlp.service.chat.child import HttpChildService

root = static.File("./html")

# uncomment only one of the bosh lines, use_raw does no xml
# parsing/serialization but is potentially less reliable
#bosh = HttpChildService(1, use_raw=True)
bosh = HttpChildService(1)

# You can limit servers with a whitelist.
# The whitelist is a list of strings to match domain names.
bosh.white_list = ['jabber.org', 'kolobiz.com']
# or a black list
# bosh.block_list = ['jabber.org', '.kolobiz.com']

print('start http-bind to local port 8073')
root.putChild('http-bind', resource.IResource(bosh))

site  = server.Site(root)

application = service.Application("botnlp")
internet.TCPServer(8073, site).setServiceParent(application)
