import modules.tools as tools


class Pod:
    def __init__(self, pod_info):
        # pod description attributes
        try:
            self.collection_id = str(pod_info['collectionId'])
            self.title = pod_info['collectionName']
            self.artist = pod_info['artistName']
            self.feed_url = pod_info['feedUrl']
            self.subtitle = ''
            self.image_url = pod_info['artworkUrl600']
            self.image_file_id = None
            self.genre_ids = pod_info['genreIds']
            self.latest_release = tools.date_to_txt(pod_info['releaseDate'])
            self.episodes = []
            self.valid = True
        except KeyError:
            self.valid = False
        
    def __repr__(self):
        txt = ''
        for attr, value in self.__dict__.items():
            if attr != 'episodes':
                txt += f"{attr}: {value}\n"
            else:
                txt += f"number of episodes: {len(self.episodes)}\n"
        return txt
    
    def get_image_path(self):
        return tools.get_pod_image_path(self.image_url, self.collection_id)
    
    def to_msg_text(self):
        msg = ''
        attributes = [('Name', 'title'),
                      ('Artist', 'artist'),
                      ('Latest release', 'latest_release')]
        for label, attr in attributes:
            msg += f"{label}: {self.__dict__[attr]}\n"
        return msg
    
    def to_msg_list(self):
        msg = f"{self.__dict__['title']} | {self.__dict__['artist']}"
        return msg
    
    def get_eps_and_subs(self):
        self.subtitle = tools.get_pod_subtitle_from_feed(self.feed_url)
        self.episodes = tools.get_ep_list_from_feed(self.feed_url)
    
    def is_chosen(self):
        if self.episodes == []:
            self.get_eps_and_subs()
        n_eps = len(tools.process_pod_feed(self.feed_url)['entries'])
        msg = f"<b>{self.title}</b>\n<i>{self.artist}</i>\n\n{self.subtitle}\n\n{n_eps} episodes, latest release was {self.latest_release}.\n"
        return msg + '\n'


class Episode:
    def __init__(self, ep_info):
        self.title = ep_info['title']
        self.subtitle, self.summary = tools.get_ep_sub_sum(ep_info)
        self.published_date = tools.process_ep_date(ep_info['published'])
        self.published_str = self.published_date.strftime('%d %B %Y')
        self.duration = tools.get_ep_duration(ep_info)
        self.link = tools.get_ep_source_link(ep_info['links'])
        self.hash = tools.hash_ep_title(self.title)
        self.shownotes = ''
        self.too_long = False
        self.file_id = None
        
    def __repr__(self):
        txt = ''
        for attr, value in self.__dict__.items():
            txt += f"{attr}: {value}\n"
        return txt
    
    def is_chosen(self):
        description = self.subtitle
        if len(description) == 0:
            description = self.summary
        if len(self.subtitle) < len(self.summary) and len(self.subtitle)!=0:
            self.too_long = True
            self.shownotes = self.summary
        
        description_tr = tools.truncate(description)
        
        if len(description_tr) < len(description):
            self.too_long = True
            self.shownotes = description
            
        msg = f"<b>{self.title}</b>\n{self.duration}, {self.published_str}\n\n{description_tr}\n\n"
        return msg
    
    def get_file_id(self, podcast, thumb_id):
        # returns a list of paths.
        # contains a single path if file size okay, else part paths
        self.file_id = tools.download_ep(self.link, self.title, podcast, thumb_id)
        return self.file_id