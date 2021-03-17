import json
from os import path
from telegram import Update
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command

CHAT_ID_FILE = "utils/connected-chats.json"


def send_awake_to_subscriber(dispatcher):
    chat_ids = _get_all_chat_ids()
    for chat_id in chat_ids:
        dispatcher.job_queue.run_once(_awake_message, 0, context=chat_id)


def _awake_message(context: CallbackContext):
    context.bot.send_message(chat_id=context.job.context, text='He hallo, i hob mi gach nei gstart.')


def _get_all_chat_ids():
    json_data = _read_chat_id_json_content()
    chat_ids = []
    for job_chat_ids in json_data:
        for chat_id in json_data[job_chat_ids]:
            if chat_id not in chat_ids:
                chat_ids.append(chat_id)
    return chat_ids


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
    json_object = _read_chat_id_json_content()
    if job_name not in json_object:
        json_object[job_name] = []
        _write_chat_id_json_content(json_object)


def _write_chat_id_json_content(json_data):
    file = open(CHAT_ID_FILE, "w")
    json.dump(json_data, file)
    file.close()


def _read_chat_id_json_content():
    if path.exists(CHAT_ID_FILE) is False:
        file = open(CHAT_ID_FILE, "w")
        json.dump({}, file)
        file.close()
    file = open(CHAT_ID_FILE, "r")
    json_object = json.load(file)
    file.close()
    return json_object


def remove_sub_from_jobs(jobs: [str], chat_id: str):
    json_data = _read_chat_id_json_content()
    for job in jobs:
        if job in json_data and chat_id in json_data[job]:
            json_data[job].remove(chat_id)
    _write_chat_id_json_content(json_data)


def register_methods_in_file(method_tuple_list, dispatcher):
    for method_tuple in method_tuple_list:
        #method_name = method_tuple[0]
        method = method_tuple[1]
        job_name = getattr(method, "_daily_run_name_decorator")
        run_time = getattr(method, "_daily_run_time_decorator")
        add_job_to_file_if_not_present(job_name)
        dispatcher.job_queue.run_daily(call_method_for_registered_chats, run_time,
                                       days=(0, 1, 2, 3, 4, 5, 6), context=method, name=job_name)


def add_sub_to_jobs(jobs: [str], chat_id: str):
    json_data = _read_chat_id_json_content()
    for job in jobs:
        json_data[job].append(chat_id)
    _write_chat_id_json_content(json_data)


@register_module()
class JobRegisterBot(AbstractModule):
    @register_command(command="start", short_desc="Start the daily bot-jobs.",
                      long_desc="Enter this command to subscribe to notifications of available jobs.\n"
                                "Specific jobs to start can be specified (see usage).",
                      usage=["/start", "/start $job1", "/start $job1 $job2"])
    def start_job(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        parameter = self.get_command_parameter("/start", update)
        json_data = _read_chat_id_json_content()
        job_names = list(json_data)

        if parameter is not None:
            parameters = parameter.split(" ")
            job_names = list(filter(lambda x: x in parameters, job_names))

        already_subbed = []
        not_subbed = []
        for job_name in job_names:
            if chat_id in json_data[job_name]:
                already_subbed.append(job_name)
            else:
                not_subbed.append(job_name)

        message = ""
        if len(already_subbed) > 0:
            message += f"Already subscribed to {str(already_subbed)}.\n"

        if len(not_subbed) > 0:
            add_sub_to_jobs(not_subbed, chat_id)
            message += f"Added subscription to {str(not_subbed)}."

        update.message.reply_text(message)

    @register_command(command="stop", short_desc="Stop the daily bot-jobs.",
                      long_desc="Enter this command to remove a subscription of a job.\n"
                                "Specific jobs to be removed can be specified otherwise "
                                "all are removed (see usage).",
                      usage=["/stop", "/stop $job1", "/stop $job1 $job2"])
    def stop_job(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        parameter = self.get_command_parameter("/stop", update)
        json_data = _read_chat_id_json_content()
        all_job_names = list(json_data)
        job_names = all_job_names

        if parameter is not None:
            parameters = parameter.split(" ")
            remove_sub = list(filter(lambda x: x in parameters, job_names))
        else:
            remove_sub = job_names

        still_subbed = []
        not_subbed = []
        removed_subs = []
        for job_name in job_names:
            if chat_id in json_data[job_name]:
                if job_name in remove_sub:
                    # remove sub
                    removed_subs.append(job_name)
                else:
                    # still subbed
                    still_subbed.append(job_name)
            else:
                not_subbed.append(job_name)

        message = ""
        if len(removed_subs) > 0:
            remove_sub_from_jobs(removed_subs, chat_id)
            message += f"Removed subscription from {str(removed_subs)}.\n"
        else:
            message += f"Nothing happened.\n"

        if len(still_subbed) > 0:
            message += f"Still subscribed to {str(still_subbed)}.\n"

        if len(not_subbed) > 0:
            message += f"Not subscribed to {str(not_subbed)}."

        update.message.reply_text(message)