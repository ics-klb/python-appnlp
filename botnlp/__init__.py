"""
BotNlp is a machine learning, conversational dialog engine.
multiple http interfaces to bot.
"""

from twisted.application import service as appService
from twisted.application import strports
from twisted.python import log

from botnlp.service.chat import session

import logging
logger = logging.getLogger('botnlp')

FIELD_AGID = 'id_pf'
is_debugger = True

__all__ = (
    'BotNlpService',
    'Service',
    'CoreApi',
    'makeService'
)

class CoreApi(object):
    def __init__(self, id:int=0):
        self._idpf = id

    def get_profileID(self):
        return self._idpf


    def set_profileID(self, id:int=0):
        self._idpf = id
        return self


class BotNlpService(appService.MultiService):
    """BotNlp parent service"""

    httpb = None

    def startService(self):
        return appService.MultiService.startService(self)

    def stopService(self):
        def cb(result):
            return appService.MultiService.stopService(self)

        d = self.service.stopService()
        d.addCallback(cb).addErrback(log.err)

        return d


class Service(appService.Service):
    """
    BotNlp generice service
    """

    def error(self, failure, body=None):
        """
        A Botnlp error has occurred
        """
        # need a better way to trap this
        if failure.getErrorMessage() != 'remote-stream-error':
            log.msg('BotNlp Error: ')
            log.msg(failure.printBriefTraceback())
            log.msg(body)
        failure.raiseException()

    def success(self, result, body=None):
        """
        If success we log it and return result
        """
        log.msg(body)
        return result

def makeService(config):
    """
    Create a BotNlp service to run
    """
    from twisted.web import server, resource, static
    from twisted.application import internet

    from botnlp.service.chat import child as service

    serviceCollection = BotNlpService()

    if config['html_dir']:
        r = static.File(config['html_dir'])
    else:
        print("The html directory is needed.")
        return

    if config['white_list']:
        service.HttpChildService.white_list = config['white_list'].split(',')

    if config['black_list']:
        service.HttpChildService.black_list = config['black_list'].split(',')

    if config['httpb']:
        b = service.HttpChildService(config['verbose'], config['polling'])
        if config['httpb'] == '':
            r.putChild(b'http-bind', resource.IResource(b))
        else:
            r.putChild(config['httpb'].encode('utf-8'), resource.IResource(b))

    if config['route']:
        service.HttpChildService.route = 'xmpp:'+config['route']

    if config['site_log_file']:
        site = server.Site(r, logPath=config['site_log_file'])
    else:
        site = server.Site(r)

    session.DIRECT_TLS = bool(config.get('directTLS'))

    if config['strports']:
        for strport in config['strports']:
            sm = strports.service(
                strport,
                site,
            )
            sm.setServiceParent(serviceCollection)

    elif config['ssl']:
        from OpenSSL import SSL
        from botnlp.utils.ssl import OpenSSLContextFactoryChaining
        ssl_context = OpenSSLContextFactoryChaining(config['ssl_privkey'],
                                                    config['ssl_cert'],
                                                    SSL.SSLv23_METHOD,)
        sm = internet.SSLServer(int(config['port']),
                                site,
                                ssl_context,
                                backlog=int(config['verbose']))
        sm.setServiceParent(serviceCollection)

    else:
        sm = internet.TCPServer(int(config['port']), site)

        sm.setServiceParent(serviceCollection)

    serviceCollection.httpb = b

    return serviceCollection