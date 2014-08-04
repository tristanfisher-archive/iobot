from __future__ import print_function
from iobot import IOBot

import zulip
import os
import shlex
import sys
from random import choice

class IOBotZulip(IOBot):

    def __init__(self, bot_name='iobot', bot_email=None, bot_api_key=None, debug=False):

        super(IOBotZulip, self).__init__(name='IOBot')

        self.debug = debug
        self.bot_name = bot_name
        self.bot_email = str(bot_email)
        self.bot_api_key = bot_api_key

        #Do this in 2 passes so we don't raise an exception when the attribute was set,
        #but the env key doesn't exist.
        if self.bot_email is None:
            try:
                self.bot_email = os.environ['ZULIP_BOT_EMAIL']
            except:
                raise Exception("Zulip bot email address was not provided and could "
                                "not be populated via the environmental variable: \nZULIP_BOT_EMAIL")

        if self.bot_api_key is None:
            try:
                self.bot_api_key = os.environ['ZULIP_API_KEY']
            except:
                raise Exception("Zulip bot api key address was not provided and could "
                                "not be populated via the environmental variable: \nZULIP_API_KEY")

        self._client = zulip.Client(email=self.bot_email, api_key=self.bot_api_key)

        # See if the action exists in the subclass before going to parent scope.
        self.bot_actions = ['help']
        self.greetings = ['hi', 'hey', 'hello', 'yo', 'sup', 'greetings', 'omg hi']  # 'omg hi' is a miss on shlex

    def user_facing(self, func):
        def register():
            if func not in self.bot_actions:
                self.bot_actions.append(func)
        register()

        return func

    # -- END OF INIT --

    #
    # Helper methods
    #
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

    #
    # User-facing bot actions
    #

    def help(self, shlexed_string):
        help_content = '''
        help:
            available zulip actions:
                {bot_actions}
        '''.format(bot_actions="\n                ".join(self.bot_actions))

        return help_content

    def say_hi(self):
        return "%s %s" % (choice(self.greetings), ':)')

    #
    # Bot action router:
    #
    def parse_handler(self, string, prefix_trigger=False):
        """
        this handler does a list lookup by grabbing the first non-whitespace string that is passed to it.

        this function is a great candidate for abstracting into a separate module.

        prefix_trigger : only parse the content when the incoming content begins with the given string.
                        this is useful for listening in a channel -- don't respond to every 'hi'
        """
        #lex and lowercase first string
        shlexed_string = shlex.split(string)
        most_significant_string = str(shlexed_string[:1][0]).lower()

        if prefix_trigger:  # is it me you're looking for?
            if most_significant_string == prefix_trigger:
                shlexed_string.pop(0)
            else:
                return None  # If we expect to get called and we don't, do nothing.

        try:
            if (str(shlexed_string[0]).lower() in self.greetings) and (len(shlexed_string) > 0):
                if prefix_trigger:  # iobot was popped off shlex (e.g. '->iobot<- hi')
                    return self.say_hi()
                if len(shlexed_string) > 1:  # hi with more text. #todo: remove?
                    if str(shlexed_string[1]).lower() == self.bot_name:  # someone is saying hi to us by name!
                        return self.say_hi()
                else:
                    return self.say_hi()
        except IndexError, e:
            sys.stderr.write('IndexError!' + str(e))
            pass  # user string was one string


        if most_significant_string in self.bot_actions:
            #If first string is in bot actions, call the method and pass it the rest of the string.
            #Leaving the method with dealing with whether or not it wants to shlex the first char.
            _func = most_significant_string
            try:  # we shouldn't get here, but don't crash
                return getattr(self, _func)(shlexed_string=shlexed_string[1:])
            except AttributeError:
                return "Command unknown.  Available actions: %s" % (", ".join(self.bot_actions))
        else:
            #if we don't have a matching bot action, return a list of actions
            return "Command unknown.  Available actions: %s" % (", ".join(self.bot_actions))

    #
    # Response mechanisms
    #

    def respond_private(self, message, _sender, response):
        # Keep from responding to ourselves

        if (_sender != self.bot_email) and (_sender is not None):
            if self.debug:
                IOBotZulip.debug_msg('Sending a private message...')
            self._client.send_message({
                "type": "private",
                "subject": message['subject'],
                "to": _sender,
                "content": response
            })

    def respond_stream(self, message, response):
        if self.debug:
            IOBotZulip.debug_msg("Sending message to a stream...")
        self._client.send_message({
            "type": "steam",
            "to": message.get('to', 'iobot'),
            "subject": self.set_return_key(obj=message, key='subject'),
            "content": response
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

                m_type = message.get('type', None)

                if self.debug: IOBotZulip.debug_msg('Sending response to: %s' % _sender)

                if m_type == 'stream' or m_type == 'channel':
                    response = self.parse_handler(message.get('content', ''), prefix_trigger=self.bot_name)
                    if response:
                        self.respond_stream(message, response)
                elif m_type == 'private':
                    response = self.parse_handler(message.get('content', ''), prefix_trigger=False)
                    if response:
                        self.respond_private(message, _sender, response)
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