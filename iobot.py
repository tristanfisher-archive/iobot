from __future__ import print_function

import sys

class IOBot(object):
    '''
    The primary class for IOBot.  Plugins should be bound to this object.
    '''

    def __init__(self, handlers=None, name='IOBot'):
        self.name = name
        self._handlers = []
        self.handlers = handlers

    #
    #  Handler functionality
    #

    #Duplicate here for now.. eventually stitch together call/get
    def call_handler(self, handler, *args, **kwargs):
        if handler in self.handlers:
            handler(args, kwargs)

    @property
    def handlers(self):
        return self._handlers

    def add_handler(self, handler):
        if (handler not in self._handlers) and (handler is not None):
            self._handlers.append(handler)

    @handlers.setter
    def handlers(self, handler):
        self.add_handler(handler)

    @handlers.deleter
    def handlers(self):
        print("Cowardly refusing to delete all handlers. "
              "Perhaps you meant to call .remove_handler('handler')?", file=sys.stderr)

    def remove_handler(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)

    #
    #  Help and User Environment
    #

    @classmethod
    def help(cls, self):
        return "IOBot is a pluggable bot.  You have reached the help method of " \
               "the IOBot base class, which doesn't really live up to its name for end users."

if __name__ == '__main__':

    _bot = IOBot()