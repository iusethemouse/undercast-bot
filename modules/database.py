"""
database.py

When imported, this module initialises an instance of the DB class, which liaises with
an SQLite database stored locally. The object, db, can be imported from this module and used
to interface with the database.
"""

import sqlite3

from . import tools, entities

POD_COLUMNS = [
        "pod_id",
        "title",
        "artist",
        "feed_url",
        "subtitle",
        "image_url",
        "image_file_id",
        "latest_release",
        "episode_count"
    ]

EP_COLUMNS = [
        "ep_id",
        "pod_id",
        "title",
        "subtitle",
        "summary",
        "published_str",
        "duration",
        "link",
        "file_id",
        "shownotes",
        "too_long"
    ]

class DB:
    def __init__(self, name="test.db"):
        self.connection = sqlite3.connect(name, check_same_thread=False)
        self.cursor = self.connection.cursor()


    def initialise(self):
        tables = {
            "podcasts": """CREATE TABLE IF NOT EXISTS podcasts
                    (pod_id INTEGER PRIMARY KEY,
                    title TEXT,
                    artist TEXT,
                    feed_url TEXT,
                    subtitle TEXT,
                    image_url TEXT,
                    image_file_id TEXT,
                    latest_release TEXT,
                    episode_count TEXT)""",

            "episodes": """CREATE TABLE IF NOT EXISTS episodes
                    (ep_id INTEGER PRIMARY KEY,
                    pod_id INTEGER,
                    title TEXT,
                    subtitle TEXT,
                    summary TEXT,
                    published_str TEXT,
                    duration TEXT,
                    link TEXT,
                    file_id TEXT,
                    shownotes TEXT,
                    too_long TEXT,
                    FOREIGN KEY(pod_id) REFERENCES podcasts(pod_id))""",

            "users": """CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY)""",

            "subscriptions": """CREATE TABLE IF NOT EXISTS subscriptions
                            (user_id INTEGER,
                            pod_id INTEGER,
                            latest_release TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(user_id),
                            FOREIGN KEY(pod_id) REFERENCES podcasts(pod_id))"""
        }

        for table in tables:
            self.cursor.execute(tables[table])

        self.connection.commit()
        print("INITIAL SETUP: done.")


    def add_podcast(self, pod_data: tuple):
        command = "INSERT INTO podcasts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(command, pod_data)
        self.connection.commit()
        print(f"ADDED PODCAST: added {pod_data[1]}.")


    def get_podcast(self, pod_id: str):
        args = (int(pod_id),)
        command = "SELECT * FROM podcasts WHERE pod_id = ?"
        try:
            print(f"LOOKING FOR PODCAST: {pod_id}.")
            return next(self.cursor.execute(command, args))
        except StopIteration:
            print(f"PODCAST NOT FOUND: {pod_id} not in database.")
            return None


    def episodes_are_stored(self, pod_id: str):
        args = (int(pod_id),)
        command = "SELECT 1 FROM episodes WHERE pod_id = ?"
        try:
            print(f"CHECKING STORED EPISODES: {pod_id}.")
            return next(self.cursor.execute(command, args))
        except StopIteration:
            print(f"NO EPISODES STORED: {pod_id}.")
            return None


    def add_episode(self, ep_data: tuple):
        command = "INSERT INTO episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(command, ep_data)
        self.connection.commit()
        print(f"ADDED EPISODE: {ep_data[2]}.")


    def get_episode(self, ep_id: str):
        args = (int(ep_id),)
        command = "SELECT * FROM episodes WHERE ep_id = ?"
        try:
            print(f"LOOKING FOR EPISODE: {ep_id}.")
            return next(self.cursor.execute(command, args))
        except StopIteration:
            print(f"EPISODE NOT FOUND: {ep_id} not in database.")
            return None


    def update_item_in_table(self, item_id, table_name, columns_to_update: dict):
        columns = list(columns_to_update.keys())
        values = list(columns_to_update.values())
        args = []
        command_start = f"UPDATE {table_name} SET "
        command_middle = "" # generated with columns_to_update
        command_end = f"WHERE {'pod_id' if table_name == 'podcasts' else 'ep_id'} = ?" # ? is item_id

        for i, column in enumerate(columns):
            command_middle += f"{column} = ?" + (", " if i < len(columns) - 1 else " ")
            args.append(values[i])

        args.append(int(item_id))
        command = command_start + command_middle + command_end

        self.cursor.execute(command, tuple(args))
        self.connection.commit()
        print(f"UPDATED TABLE {table_name.upper()}: item {item_id}.")


    def get_all_podcasts(self):
        command = "SELECT * FROM podcasts"
        try:
            print("GETTING ALL PODCASTS.")
            return [x for x in self.cursor.execute(command)]
        except StopIteration:
            print("NO PODCASTS STORED.")
            return None


    def get_all_episodes(self, pod_id):
        command = "SELECT * FROM episodes WHERE pod_id = ?"
        args = (int(pod_id),)
        try:
            print(f"GETTING ALL EPISODES: for podcast {pod_id}.")
            return [x for x in self.cursor.execute(command, args)]
        except StopIteration:
            print(f"NO EPISODES STORED: for podcast {pod_id}.")
            return None


    def is_subscribed_to(self, user_id, pod_id):
        args = (int(user_id), int(pod_id),)
        command = "SELECT 1 FROM subscriptions WHERE user_id = ? AND pod_id = ?"
        try:
            print(f"CHECKING SUBSCRIPTION: user {user_id}, podcast {pod_id}.")
            _ = next(self.cursor.execute(command, args))
            return True
        except StopIteration:
            print(f"NOT SUBSCRIBED: user {user_id}, podcast {pod_id}.")
            return False


    def subscribe_user_to_podcast(self, user_id, pod_id, latest_release):
        args = (int(user_id), int(pod_id), latest_release,)
        command = "INSERT INTO subscriptions VALUES (?, ?, ?)"

        self.cursor.execute(command, args)
        self.connection.commit()
        print(f"USER SUBSCRIBED TO PODCAST: user {user_id}, podcast {pod_id}.")


    def unsubscribe_user_from_podcast(self, user_id, pod_id):
        args = (int(user_id), int(pod_id),)
        command = "DELETE FROM subscriptions WHERE user_id = ? AND pod_id = ?"

        self.cursor.execute(command, args)
        self.connection.commit()
        print(f"USER UNSUBSCRIBED FROM PODCAST: user {user_id}, podcast {pod_id}.")


    def get_all_subscriptions(self, user_id):
        args = (int(user_id),)
        command = "SELECT pod_id FROM subscriptions WHERE user_id = ?"

        try:
            print(f"GETTING SUBSCRIPTIONS FOR USER: {user_id}.")
            return [x for x in self.cursor.execute(command, args)]
        except StopIteration:
            print(f"NO SUBSCRIPTIONS FOR USER: {user_id}.")
            return None


db = DB("bot.db")
db.initialise()