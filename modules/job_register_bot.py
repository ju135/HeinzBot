import datetime
import json
from telegram import Update
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from modules.default_module import DefaultModule
from utils.decorators import register_module, register_command

CHAT_ID_FILE = "utils/connected-chats.json"

def call_method_for_registered_chats(context: CallbackContext):
    # the job-context contains the method to call
    method_to_call = context.job.context
    job_name = context.job.name
    # get subscribed message-ids for this job
    chat_ids = get_subscribed_chat_ids(job_name)

    for chat_id in chat_ids:
        method_to_call(context, chat_id)


def get_subscribed_chat_ids(job_name: str):
    f = open(CHAT_ID_FILE, "r")
    chat_id_data = json.load(f)
    if job_name in chat_id_data:
        return chat_id_data[job_name]
    return []


def add_job_to_file_if_not_present(job_name: str):
    file = open(CHAT_ID_FILE, "r")
    json_object = json.load(file)
    file.close()
    if job_name not in json_object:
        json_object[job_name] = []
        file = open(CHAT_ID_FILE, "w")
        json.dump(json_object, file)
        file.close()


def _read_chat_id_json_content():
    file = open(CHAT_ID_FILE, "r")
    json_object = json.load(file)
    file.close()
    return json_object


if __name__ == "__main__":
    add_job_to_file_if_not_present("heinz")


def register_methods_in_file(method_tuple_list, dispatcher):
    for method_tuple in method_tuple_list:
        #method_name = method_tuple[0]
        method = method_tuple[1]
        job_name = getattr(method, "_daily_run_name_decorator")
        run_time = getattr(method, "_daily_run_time_decorator")
        add_job_to_file_if_not_present(job_name)
        dispatcher.job_queue.run_daily(call_method_for_registered_chats, run_time,
                                       days=(0, 1, 2, 3, 4, 5, 6), context=method, name=job_name)


@register_module()
class JobRegisterBot(AbstractModule):
    @register_command(command="start", text="To start the daily jobs")
    def start_job(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        json_data = _read_chat_id_json_content()
        already_subbed = list(filter(lambda x: chat_id in x, json_data)) # TODO ERROR - No error handlers are registered, logging exception.
        not_subbed = list(filter(lambda x: chat_id not in x, json_data))

        # read all daily jobs

        context.bot.send_message(chat_id, "Registered")