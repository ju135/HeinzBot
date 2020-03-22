from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.members import getName, getTOP
from modules.abstract_module import AbstractModule
from modules.default_module import DefaultModule
from utils.decorators import register_module, register_command, register_callback_query_handler
from utils.random_text import get_random_string_of_messages_file

currentUpdate = None  # the current invitation we are editing
coffee_message_constants_file = "constants/messages/coffee_messages.json"


@register_module()
class CoffeeBot(AbstractModule):
    # sends a coffee invitation with inline keyboard
    @register_command(command="coffee", short_desc="Ask for coffe",
                      long_desc="Sends a request to the group for coffee. Is really useful if you are tired.",
                      usage=["/coffee"])
    def sendCoffeeInvitation(self, update: Update, context: CallbackContext):
        userid = update.message.from_user.id
        name = getName(userid)
        top = getTOP(userid)

        keyboard = [
            [InlineKeyboardButton("TOP {}".format(top), callback_data=str("coffee:host")),
             InlineKeyboardButton("wo anders", callback_data=str("coffee:other")),
             InlineKeyboardButton("FH", callback_data=str("coffee:FH"))]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        firstText = get_random_string_of_messages_file(coffee_message_constants_file, ["starter"]).replace("$", name)
        update.message.reply_text(firstText, reply_markup=markup)
        global currentUpdate  # set the current update users will reply to
        currentUpdate = update

    # will send a variety of coffee stickers
    def sendCoffeeSticker(self, update: Update, context: CallbackContext):
        # chatid = update.message.chat.id
        pass

    """called when a location button in the inline keyboard was clicked,
    will update the message with the location"""

    @register_callback_query_handler(command="coffee")
    def sendCoffeeLocation(self, update: Update, context: CallbackContext):
        query = update.callback_query
        clickingUserID = query.from_user.id

        if currentUpdate == None or clickingUserID == currentUpdate.message.from_user.id:
            text = query.message.text
            text += "\n\n"

            end = get_random_string_of_messages_file(coffee_message_constants_file,
                                                     ["ends", query.data.replace('coffee:', '')])
            if "host" in query.data:  # if hosting, fill in the name, too.
                end = end.replace("$", str(getTOP(clickingUserID)))
            text += end

            query.edit_message_text(text=text + "  ")
        else:
            context.bot.send_message(chat_id=currentUpdate.message.chat.id,
                                     text="Herst {}, hab i mid dia gredt?".format(getName(clickingUserID)))
