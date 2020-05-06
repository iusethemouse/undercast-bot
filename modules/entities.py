"""Classes for podcasts and episodes."""

import modules.tools as tools

class Pod:
    """
    A class used to represet a Podcast.

    Basic attributes are acquired from the iTunes json dictionary for this particular
    podcast. Upon selection, further attributes are acquired by parsing the podcast's feed.

    """

    def __init__(self, pod_info: dict):
        """
        pod_info is an element of the "results" list of the iTunes json dictionary.
        A podcast is not valid if any of the below attributes are not keys in pod_info.
        """

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
        """
        This method is called by print(Pod).
        It prints out all attributes and their values, for debugging purposes.
        """

        txt = ''
        for attr, value in self.__dict__.items():
            if attr != 'episodes':
                txt += f"{attr}: {value}\n"
            else:
                txt += f"number of episodes: {len(self.episodes)}\n"
        
        return txt
    

    def get_image_path(self):
        """
        This method is called if self.image_file_id is None.
        The artwork image is downloaded and stored locally, its path is returned.
        """

        return tools.get_pod_image_path(self.image_url, self.collection_id)

    
    def to_msg_list(self):
        """
        This method generates a message of format "pod.title | pod.artist".
        It is called when processing the iTunes json file in order to generate
        a list of inline buttons displaying search results.
        """

        return f"{self.__dict__['title']} | {self.__dict__['artist']}"
    

    def get_eps_and_subs(self):
        """
        This method is only called either manually or from the self.is_chosen()
        method. Podcast feed is parsed to acquire the subtitle/summary, and episodes.
        Each episode in self.episodes is an Episode object.
        """

        self.subtitle = tools.get_pod_subtitle_from_feed(self.feed_url)
        self.episodes = tools.get_ep_list_from_feed(self.feed_url)
    

    def is_chosen(self):
        """
        This method is called when the user selects a podcast from the search results.
        Subtitle/summary and episodes are acquired from the podcast feed, and a display
        message is generated.
        """

        if self.episodes == []:
            self.get_eps_and_subs()
        n_eps = len(tools.process_pod_feed(self.feed_url)['entries'])
        msg = f"<b>{self.title}</b>\n<i>{self.artist}</i>\n\n{self.subtitle}\n\n{n_eps} episodes, latest release was {self.latest_release}.\n"
        
        return msg + '\n'


class Episode:
    """
    A class used to represent an Episode.

    A lot of processing and parsing is done upon initialisation. All attributes
    are acquired from the ep_info dictionary, which is an element of the "entries"
    list in a podcast feed.

    """

    def __init__(self, ep_info: dict):
        """
        ep_info is parsed to acquire most of the below attributes, after
        which further processing is done.
        self.too_long refers to the length of self.subtitle for the purposes
        of figuring out self.shownotes.
        """

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
        """
        This method is called by print(Episode).
        It prints out all attributes and their values, for debugging purposes.
        """

        txt = ''
        for attr, value in self.__dict__.items():
            txt += f"{attr}: {value}\n"
        
        return txt
    

    def is_chosen(self):
        """
        This method is called when an episode is selected from the episode list.
        A display message is generated, and, if appropriate, self.shownotes are assigned.
        """

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
    

    def get_file_id(self, podcast: str, thumb_id: str):
        """
        This method is called when the user actions a first-time download for an episode.
        File ID is returned for the episode after the secondary process uploads the .mp3 file
        to Telegram's servers.

        Currently this method is blocking while it awaits response from the secondary process
        upon completion of upload.
        TODO: implement an async version of this method.
        """
        # returns a list of paths.
        # contains a single path if file size okay, else part paths
        self.file_id = tools.download_ep(self.link, self.title, podcast, thumb_id)
        
        return self.file_id