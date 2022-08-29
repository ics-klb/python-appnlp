
from twisted.web import server, resource, static
from twisted.application import service, internet

class Worker(object):
    """
    A conversational dialog chat bot.
    """
    host = ''
    port = ''

    def __init__(self, cursor = 'default', **kwargs):
        self.cursor = cursor
        # Logic adapters used by the chat bot
        self.logic_adapters = []

    def start_daemon(self, host='127.0.0.1', port=8073):
        print('start_daemon')
        self.host = host
        self.port = port
        self.on_service()

    def on_service(self) -> None:
        from .service.chat.child import HttpChildService

        print('service: ', "host: %s, port: %s." % (self.host, self.port))
        root = static.File("./html")

        # uncomment only one of the bosh lines, use_raw does no xml
        # parsing/serialization but is potentially less reliable
        #bosh = HttpChildService(1, use_raw=True)
        bosh = HttpChildService(1)

        # You can limit servers with a whitelist.
        # The whitelist is a list of strings to match domain names.
        # bosh.white_list = ['jabber.org', 'thetofu.com']
        # or a black list
        # bosh.block_list = ['jabber.org', '.thetofu.com']

        root.putChild('http-bind', resource.IResource(bosh))
        site = server.Site(root)

        application = service.Application("botnlp")
        internet.TCPServer(self.port, site).setServiceParent(application)
