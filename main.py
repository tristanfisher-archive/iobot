from plugin_zulip import IOBotZulip


if __name__ == '__main__':

    test_bot = IOBotZulip()
    test_bot.callback(callback_type='message')