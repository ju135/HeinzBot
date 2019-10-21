from telegram.ext import CommandHandler


class DefaultModule():
    mutedAccounts = list()

    def add_command(self, dp):
        instance = DefaultModule()
        dp.add_handler(CommandHandler('mute', instance.mute))

    def mute(self, bot, update):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/mute ', '')
            bot.send_message(chat_id=update.message.chat_id,
                             text=(person + ' wird gemutet!'))
            self.mutedAccounts.append(person)
        else:
            update.message.reply_text('Sry du deafst kan muten..')

    def has_rights(self, update):
        if update.message.from_user.name in self.mutedAccounts:
            update.message.reply_text(
                '..hot wer wos gsogt?')
            return False
        if update.message.from_user.last_name in self.mutedAccounts:
            update.message.reply_text(
                '..hot wer wos gsogt?')
            return False
        return True

    def get_command_parameter(self, command: str, update) -> str:
        text = update.message.text
        b = update.message.bot.name
        if text.startswith(command + " "):
            return text[len(command) + 1:]
        if text.startswith(command + b + " "):
            return text[len(command + b) + 1:]
