from plugin_zulip import IOBotZulip

if __name__ == '__main__':

    test_bot = IOBotZulip(bot_email='my_bot_email_address@example.org', bot_api_key='zulip_api_key')
    test_bot.callback(callback_type='message')