from __future__ import print_function

import zulip
import os
import sys

class IOBotZulip(object):

    def __init__(self, bot_email=None, bot_api_key=None, debug=True):
        self.debug = debug
        self.bot_email = str(bot_email)
        self.bot_api_key = bot_api_key

        #Do this in 2 passes so we don't raise an exception when the attribute was set,
        #but the env key doesn't exist.
        if self.bot_email is None:
            try:
                self.bot_email = os.environ['ZULIP_BOT_EMAIL']
            except:
                raise Exception("Zulip bot email address was not provided and could "
                                "not be populated via the environmental variable: \n ZULIP_BOT_EMAIL")

        if self.bot_api_key is None:
            try:
                self.bot_api_key = os.environ['ZULIP_API_KEY']
            except:
                raise Exception("Zulip bot api key address was not provided and could "
                                "not be populated via the environmental variable: \n ZULIP_API_KEY")

        self._client = zulip.Client(email=self.bot_email, api_key=self.bot_api_key)

    # -- END OF INIT --

    #shim for more sophisticated logging later.
    @staticmethod
    def debug_msg(prefix='[DEBUG]>>> ', *args, **kwargs):
        try:
            print("%s %s" % (prefix, args), file=sys.stdout)
            for x, y in kwargs.iteritems():
                print("%s %s : %s" % (prefix, x, y), file=sys.stdout)
        except TypeError, e:  # don't break on operand issues
            print(">>>> Caught error on debug_msg: " + str(e), file=sys.stderr)

    def set_return_key(self, obj, key, default='iobot'):
        if obj.get(key) is None:
            obj.update(key=default)

        return obj.get(key)

    def respond_private(self, message, _sender):
        # Keep from responding to ourselves
        if (_sender != self.bot_email) and (_sender is not None):
            print(">>>>>>>>>>>>>%s" % _sender)
            if self.debug:
                IOBotZulip.debug_msg('Sending a private message...')
            self._client.send_message({
                "type": "private",
                "subject": message['subject'],
                "to": _sender,
                "content": message['content']
            })

    def respond_stream(self, message):
        if self.debug:
            IOBotZulip.debug_msg("Sending message to a stream...")
        self._client.send_message({
            "type": "steam",
            "to": message.get('to', 'iobot'),
            "subject": self.set_return_key(obj=message, key='subject'),
            "content": message['content']
        })

    def respond(self, message=None, channel=None, content=None):

        if self.debug:
            debug_output = {
                'message': message,
                'channel': channel,
                'content': content
            }
            IOBotZulip.debug_msg('send_message() debug: ', debug_output)

        #suuuuper cheap version of types.NoneType
        if id(message) is not id(None):

            _sender = message['sender_email']

            #self.bot_email is a str, cast unicode str(_sender) and check that _sender isn't None.
            if (str(_sender) != self.bot_email) and (_sender is not None):

                # recursion is happening here

                m_type = message.get('type', None)

                if m_type == 'stream' or m_type == 'channel':
                    self.respond_stream(message)
                elif m_type == 'private':
                    self.respond_private(message, _sender)
                else:
                    pass
                return

            else:
                if self.debug:
                    IOBotZulip.debug_msg("send_message()-> Sender email was >> %s <<.  Refusing to go into a recursive loop." % _sender)

    def callback(self, callback_type='message'):

        action = self.respond

        if callback_type == 'event':
            sys.stderr.write("callback()->callback_type: event handler not yet implemented!")
            self._client.call_on_each_event(lambda message: sys.stdout.write(str(message) + "\n"))
        else:
            self._client.call_on_each_message(lambda msg: action(msg))

    bind = callback


