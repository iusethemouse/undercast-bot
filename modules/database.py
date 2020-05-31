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
        podcasts = """CREATE TABLE IF NOT EXISTS podcasts
                    (pod_id INTEGER PRIMARY KEY,
                    title TEXT,
                    artist TEXT,
                    feed_url TEXT,
                    subtitle TEXT,
                    image_url TEXT,
                    image_file_id TEXT,
                    latest_release TEXT,
                    episode_count TEXT)"""
        self.cursor.execute(podcasts)

        episodes = """CREATE TABLE IF NOT EXISTS episodes
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
                    FOREIGN KEY(pod_id) REFERENCES podcasts(pod_id))"""
        self.cursor.execute(episodes)

        self.connection.commit()


    def add_podcast(self, pod_data: tuple):
        command = "INSERT INTO podcasts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(command, pod_data)
        self.connection.commit()
        print(f"Added {pod_data[1]} to podcasts table!\n")


    def get_podcast(self, pod_id: str):
        args = (int(pod_id),)
        command = "SELECT * FROM podcasts WHERE pod_id = ?"
        try:
            return next(self.cursor.execute(command, args))
        except StopIteration:
            print(f"Podcast {pod_id} not in database.\n")
            return None


    def episodes_are_stored(self, pod_id: str):
        args = (int(pod_id),)
        command = "SELECT 1 FROM episodes WHERE pod_id = ?"
        try:
            return next(self.cursor.execute(command, args))
        except StopIteration:
            return None


    def add_episode(self, ep_data: tuple):
        command = "INSERT INTO episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(command, ep_data)
        self.connection.commit()
        print(f"Added episode {ep_data[2]} to episodes table!\n")


    def get_episode(self, ep_id: str):
        args = (int(ep_id),)
        command = "SELECT * FROM episodes WHERE ep_id = ?"
        try:
            print(f"Getting episode with ID {ep_id}...\n")
            return next(self.cursor.execute(command, args))
        except StopIteration:
            print(f"Episode {ep_id} not in database.\n")
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
        print(f"Successfully updated item {item_id} in {table_name}.")


    def all_podcasts(self):
        command = "SELECT * FROM podcasts"
        try:
            print("Getting all podcasts...")
            return [x for x in self.cursor.execute(command)]
        except StopIteration:
            print("Podcasts table is empty.\n")
            return None


    def get_all_episodes(self, pod_id):
        command = "SELECT * FROM episodes WHERE pod_id = ?"
        args = (pod_id,)
        try:
            print(f"Getting all episodes for podcast {pod_id}...\n")
            return [x for x in self.cursor.execute(command, args)]
        except StopIteration:
            print(f"Found no episodes for podcast {pod_id}.\n")
            return None


db = DB("bot.db")
db.initialise()