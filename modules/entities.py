"""
entities.py

Podcast and Episode classes that represent podcasts and episodes respectively.
"""

from . import tools

class Pod:
    def __init__(self, pod_info):
        try:
            self.pod_id = str(pod_info['collectionId'])
            self.title = pod_info['collectionName']
            self.artist = pod_info['artistName']
            self.feed_url = pod_info['feedUrl']
            self.subtitle = None
            self.image_url = pod_info['artworkUrl600']
            self.image_file_id = None
            self.genres = pod_info['genres']
            self.latest_release = tools.prettify_latest_release_date(pod_info['releaseDate'])
            self.episode_count = pod_info['trackCount']
            self.episodes = None
            self.valid = True
        except KeyError:
            self.valid = False
        

    def __repr__(self):
        result = ''
        for attr, value in self.__dict__.items():
            result += f"{attr}: {value}\n"
        return result


    def generate_description(self):
        description = f"<b>{self.title}</b>\n<i>{self.artist}</i>\n\n{self.subtitle}\n\n{self.episode_count} episodes, latest release was {self.latest_release}.\n\n"
        return description


class Episode:
    def __init__(self, ep_info):
        self.title = ep_info['title']
        self.subtitle, self.summary = tools.get_episode_subtitle_and_summary(ep_info)
        self.published_date = tools.process_ep_date(ep_info['published'])
        self.published_str = self.published_date.strftime('%d %B %Y')
        self.duration = tools.get_ep_duration(ep_info)
        self.link = tools.get_ep_source_link(ep_info['links'])
        self.hash = tools.hash_string(self.title)
        self.shownotes = ''
        self.too_long = False
        self.file_id = None
        

    def __repr__(self):
        txt = ''
        for attr, value in self.__dict__.items():
            txt += f"{attr}: {value}\n"
        return txt
    

    def is_chosen(self):
        description = self.summary if len(self.subtitle) == 0 else self.subtitle
        # if len(description) == 0:
        #     description = self.summary
        if 0 < len(self.subtitle) < len(self.summary):
            self.too_long = True
            self.shownotes = self.summary
        
        description_truncated = tools.truncate(description)
        
        if len(description_truncated) < len(description):
            self.too_long = True
            self.shownotes = description
            
        msg = f"<b>{self.title}</b>\n{self.duration}, {self.published_str}\n\n{description_truncated}\n\n"
        return msg
    

    def get_file_id(self, pod_title, thumb_id):
        self.file_id = tools.download_ep(self.link, self.hash, self.title, pod_title, thumb_id)
        return self.file_id