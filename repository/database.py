import pymysql.cursors
from utils.decorators import Singleton
from datetime import datetime
import os
from dotenv import load_dotenv
from definitions import ROOT_DIR


@Singleton
class Database:
    connection = None

    def __init__(self):
        # Connect to the database
        load_dotenv(dotenv_path=ROOT_DIR + "/.env")
        self.connect()
        self.create_media_table()
        self.create_remind_me_jobs_table()

    def get_env_var(self, key):
        return os.getenv(key)

    def connect(self):
        db = self.get_env_var("MYSQL_DATABASE")
        user = self.get_env_var("MYSQL_USER")
        pw = self.get_env_var("MYSQL_PASSWORD")
        host = self.get_env_var("DB_HOST")

        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          password=pw,
                                          database=db,
                                          cursorclass=pymysql.cursors.DictCursor)

    def create_remind_me_jobs_table(self):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = """create table if not exists remind_me_jobs
                            (  
                            id int auto_increment
                                primary key,
                            chat_id varchar(30) not null,
                            message_id varchar(30) not null,
                            user_id varchar(30) null,
                            username varchar(30) null,
                            specified_message varchar(255) null,
                            trigger_time timestamp not null,
                            created_at timestamp null
                        );"""

                cursor.execute(sql)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def insert_into_remind_me_jobs(self, chat_id, message_id, user_id, username, specified_message, trigger_time):
        self.connect()

        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `remind_me_jobs` (`chat_id`, `message_id`, `user_id`, `username`, " \
                      "`specified_message`, `trigger_time`, `created_at`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (chat_id, message_id, user_id, username, specified_message, trigger_time, datetime.now()))

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

    def create_media_table(self):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = """create table if not exists media
                            (  
                            id int auto_increment
                                primary key,
                            deleted bool default false null,
                            chat_id varchar(30) null,
                            username varchar(30) null,
                            user_id varchar(30) null,
                            created_at timestamp null,
                            message_id varchar(30) null,
                            type varchar(20) null,
                            command varchar(255) null,
                            searchtext varchar(255) null
                        );"""

                cursor.execute(sql)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def insert_into_media(self, chat_id, message_id, command, username, user_id, type, searchtext):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `media` (`chat_id`, `message_id`, `command`, `username`, `user_id`, `created_at`, `type`, `searchtext`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (chat_id, message_id, command, username, user_id, datetime.now(), type, searchtext.lower()))

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
