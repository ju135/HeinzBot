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
        self.create_reddit_table()

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

    def create_reddit_table(self):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = """create table if not exists reddit
                            (  
                            id int auto_increment
                                primary key,
                            deleted bool default false null,
                            chat_id int null,
                            username varchar(30) null,
                            created_at timestamp null,
                            message_id varchar(30) null,
                            command varchar(255) null
                        );"""

                cursor.execute(sql)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def insert_into_reddit(self, chat_id, message_id, command, username):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `reddit` (`chat_id`, `message_id`, `command`, `username`, `created_at`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (chat_id, message_id, command, username, datetime.now()))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def get_from_reddit_by_command(self, chat_id, command):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `chat_id`, `message_id` FROM `reddit` WHERE `chat_id`=%s AND `command` LIKE CONCAT('%%',%s,'%%');"
                cursor.execute(sql, (chat_id, command))
                result = cursor.fetchall()
                print(result)

    def delete_from_reddit_by_command(self, chat_id, command):
        self.connect()
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE reddit SET deleted = true WHERE chat_id=%s AND command LIKE '%" + command + "%';"
                cursor.execute(sql, (chat_id,))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
