from datetime import time

from pony.orm import *

db = Database()


class Media(db.Entity):
    id = PrimaryKey(int, auto=True)
    deleted = Required(bool)
    chat_id = Optional(str)
    username = Optional(str)
    user_id = Optional(str)
    created_at = Optional(time)
    message_id = Optional(str)
    type = Optional(str)
    command = Optional(str)
    searchtext = Optional(str)
