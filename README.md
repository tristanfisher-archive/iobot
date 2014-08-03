#IO Bot
======

IO Bot is _YAZBWAHS_ (Yet Another [Zulip](https://zulip.com) Bot Written At [Hacker School](http://hackerschool.com)).

###Features:

IO Bot will-be/is a collection of [objects](https://docs.python.org/2/tutorial/classes.html). -- feel free to simply use it for its [modules](https://docs.python.org/2/tutorial/modules.html).

###How to use:

To connect IO Bot to Zulip, write a simple Python script:

	from plugin_zulip import IOBotZulip

	if __name__ == '__main__':
    	test_bot = IOBotZulip(bot_email='bot@example.org', bot_api_key='zulip_api_key')
    	test_bot.callback(callback_type='message')
    	
###Plugins:

#####Zulip:

You can pass the bot's email address and API key via environmental variables:

- ZULIP_BOT_EMAIL
- ZULIP_API_KEY


####Python Version:

  IoBot is written for Python 2.7 due to some underlying dependencies. 

####To Do:

- Add pluggable handlers. This will work via the following syntax: `test_bot.add_handler('stackoverflow')`.
- Add tests.
- Separate logging into a separate module.