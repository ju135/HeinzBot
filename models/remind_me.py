from datetime import time

from pony.orm import *

db = Database()


class RemindMe(db.Entity):
    id = PrimaryKey(int, auto=True)
    chat_id = Required(str)
    message_id = Required(str)
    user_id = Required(str)
    username = Required(str)
    specified_message = Required(str)
    trigger_time = Required(time)
    created_at = Optional(time)


