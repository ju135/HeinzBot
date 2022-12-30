import os
from datetime import datetime

from dotenv import load_dotenv
from pony import orm
from pony.orm import *

from definitions import ROOT_DIR
from utils.decorators import Singleton


@Singleton
class Database:
    connection = None

    def __init__(self):
        # Connect to the database
        print("Starting db")
        load_dotenv(dotenv_path=ROOT_DIR + "/.env")
        self.connect()

    def get_env_var(self, key):
        return os.getenv(key)

    def connect(self):
        db = self.get_env_var("MYSQL_DATABASE")
        user = self.get_env_var("MYSQL_USER")
        pw = self.get_env_var("MYSQL_PASSWORD")
        host = self.get_env_var("DB_HOST")

        self.connection = orm.Database()
        sql_debug(True)

        self.connection.bind(provider='mysql',
                             host=host,
                             create_db=True,
                             user=user,
                             password=pw,
                             db=db)
        self.connection.generate_mapping(create_tables=True)

    def insert_into_remind_me_jobs(self, chat_id, message_id, user_id, username, specified_message, trigger_time):
        self.connect()

        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `remind_me_jobs` (`chat_id`, `message_id`, `user_id`, `username`, " \
                      "`specified_message`, `trigger_time`, `created_at`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (
                    chat_id, message_id, user_id, username, specified_message, trigger_time, datetime.now()))

            remind_me_job_id = self.connection.insert_id()
            self.connection.commit()

        return remind_me_job_id

    def get_remind_me_job_by_id(self, db_job_id):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `remind_me_jobs` WHERE `id`=%s LIMIT 1;"
                cursor.execute(sql, db_job_id)
                result = cursor.fetchone()
                return result

    def get_upcoming_remind_me_jobs(self):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT trigger_time, id FROM `remind_me_jobs` WHERE `trigger_time`>%s;"
                cursor.execute(sql, datetime.now())
                result = cursor.fetchall()
                return result

    def delete_remind_me_job_by_id(self, db_job_id):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM `remind_me_jobs` WHERE `id`=%s;"
                cursor.execute(sql, db_job_id)
            self.connection.commit()

    def delete_all_expired_remind_me_jobs(self):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM `remind_me_jobs` WHERE `trigger_time`<%s;"
                cursor.execute(sql, datetime.now())
            self.connection.commit()

    def insert_into_media(self, chat_id, message_id, command, username, user_id, type, searchtext):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `media` (`chat_id`, `message_id`, `command`, `username`, `user_id`, `created_at`, `type`, `searchtext`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (
                    chat_id, message_id, command, username, user_id, datetime.now(), type, searchtext.lower()))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def get_from_media_by_command(self, chat_id, searchtext):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `chat_id`, `message_id` FROM `media` WHERE `chat_id`=%s AND `deleted`=false AND `searchtext` LIKE CONCAT('%%',%s,'%%');"
                cursor.execute(sql, (chat_id, searchtext.lower()))
                result = cursor.fetchall()
                return result

    def delete_from_media_by_command(self, chat_id, searchtext):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE media SET deleted = true WHERE `chat_id`=%s AND `searchtext` = %s;"
                cursor.execute(sql, (chat_id, searchtext.lower(),))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
