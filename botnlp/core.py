# -*- coding: utf-8 -*-
from .functions import getsetup_config

class BotCore():

    cfg = None

    statement = None

    def __init__(self):
        self.cfg = getsetup_config()

    def get_config(self, name):
        return self.cfg[name]

    def set_statement(self):
        return self.statement

    def set_statement(self, statement='Hello'):
        self.statement = statement

    def get_response(self):
        pass

    def get_response_time(self, statement='Hello'):
        """
        Returns the amount of time taken for a given
        chat bot to return a response.

        :param botchat: A chat bot instance.
        :type botchat: BotCore

        :returns: The response time in seconds.
        :rtype: float
        """
        import time

        start_time = time.time()

        self.set_statement(self.statement)
        self.get_response()

        return time.time() - start_time

