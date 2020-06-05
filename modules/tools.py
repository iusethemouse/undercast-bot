"""
tools.py

Helper functions for various operations and computations required by bot routies.
"""

import requests
import re
import feedparser
from pathlib import Path
import os
from hashlib import sha256
from datetime import datetime, timedelta
from math import fabs
import urllib.request
import shutil
import time
import uuid

# Local modules
from .entities import Pod, Episode
from .database import POD_COLUMNS, EP_COLUMNS

# Globals
IMG_ROOT = Path('artwork/')
EP_ROOT = Path('episodes/')
MAX_SEARCH_RESULTS = 6


def get_search_json(search_term: str):
    """
    Returns an iTunes json containing search results.

    json = {resultCount: int, results: [podcasts]}
    """
    max_results = str(MAX_SEARCH_RESULTS)
    itunes_url = "https://itunes.apple.com/search?&media=podcast&limit="+max_results+"&term="
    search_url = itunes_url + search_term
    json_result = requests.get(search_url).json()
    
    return json_result


def json_to_pods(results: list):
    """
    Converts a list of dicts into a list of Pod objects.
    """
    pods = []
    for entry in results:
        pod = Pod(entry)
        if pod.valid:
            pods.append(pod)

    return pods


def prettify_latest_release_date(date_str):
    """
    Converts an iTunes-formatted date into a short note about when the last episode
    was released.
    """
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    date_diff = datetime.now() - date
    day_diff = int(fabs(date_diff.days))
    
    if day_diff == 0:
        txt = 'less than a day ago'
    elif day_diff == 1:
        txt = '1 day ago'
    elif day_diff > 356:
        txt = 'more than a year ago'
    else:
        txt = f"{day_diff} days ago"
    
    return txt


def download_artwork(img_url, pod_id):
    """
    Downloads the artwork for specified podcast and returns its path.

    The artwork file is then deleted by parent process to save space, while its fileID is stored.
    """
    ext = str(pod_id) + '.jpg'
    root = IMG_ROOT
    
    if not root.exists():
        os.makedirs(IMG_ROOT)
    if not (root/ext).exists():
        img_data = requests.get(img_url)
        with open(root/ext, 'wb') as im_file:
            im_file.write(img_data.content)
    
    return root/ext


def parse_feed(feed_url):
    """
    Parses RSS feed. Returns a tuple of podcast information as a dict and a list of episode dicts.
    """
    feed_root = feedparser.parse(feed_url)

    return feed_root['feed'], feed_root['entries']


def get_pod_subtitle_from_feed(feed):
    """
    Gets a podcast subtitle. It is preferable to use the 'subtitle' field if it exists.
    In some cases it exists but is set to the empty string, in which case 'summary' also works.
    """
    try:
        text = feed['subtitle'] if feed['subtitle'] != '' else feed['summary']
    except KeyError:
        text = feed['subtitle']
        
    return clean_html(text)


def get_episode_subtitle_and_summary(ep_info):
    """
    Episode subtitle and summary are used to determine if an episode has show notes.

    Because of the inconsistencies among different podcasts' feeds, certain cases will
    have the 'subtitle' field, and others won't. In that case 'summary' becomes the only
    episode description available, which also later gets split if longer than 1000 characters.
    """
    try:
        subtitle = clean_html(ep_info["subtitle"])
    except KeyError:
        subtitle = ""
    summary = clean_html(ep_info["summary"])

    return subtitle, summary


def get_ep_duration(ep):
    """
    Due to inconsistencies in RSS feeds, some episodes don't have the duration listed, in which
    case this returns '-'.

    There are two ways that duration gets represented in feeds: hh:mm:ss, or the number of seconds.
    This gets rid of trailing zeros to conserve space, as the duration is displayed in the episode list view.

    The returned string is of format 1h 20m
    """
    res = '-'
    if 'itunes_duration' in ep:
        dur = ep['itunes_duration']
        if ':' not in dur:
            dur = str(timedelta(seconds=int(dur)))
        dur_stripped = re.sub(r'^0{1,2}:*|(?<=:)0', '', dur[:-3])
        res = re.sub(r':', 'h ', dur_stripped) + 'm'
    
    return res


def get_ep_source_link(link_list):
    """
    Looks for a link that contains the '.mp3' extension.
    """
    for link_dict in link_list:
        if '.mp3' in link_dict['href']:
            return link_dict['href']


def generate_uuid():
    """
    Returns a 5-digit randomly generated int.
    """
    return str(uuid.uuid4().int)[:5]


def hash_string(s):
    """
    Returns a numeric sha256 hash of a string.
    """
    return int(sha256(s.encode('UTF-8')).hexdigest(), 16) % 10**12


def process_ep_date(date_str):
    """
    Parses episode's release date. There are two most commong date formats in RSS feeds
    that this accounts for.
    """
    try:
        res = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        res = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %Z")
        
    return res


def create_paginated_list(res_per_page, n_items):
    """
    Creates a list of pages that contain indices of items to list.
    """
    n_chunks = n_items // res_per_page
    res_list = [res_per_page * i for i in range(1, n_chunks + 1)]
    remainder = n_items - res_per_page * n_chunks
    
    if remainder != 0:
        res_list.append(n_items)
        
    return res_list


def download_ep(link, ep_id, title, pod_title, thumb_id):
    """
    Downloads the audio file, then waits for start_file_uploader.php to upload the file
    and provide its Telegram fileID. The fileID is returned.
    """ 
    root = EP_ROOT
    to_php = Path("episode_uploader/episodes_to_send/")
    ep_id = str(ep_id)
    ext = ep_id + '.mp3'
    ext_txt = ep_id + '.txt'
    ext_data = ep_id + '_data.txt'

    if not root.exists():
        os.makedirs(root)
    if not to_php.exists():
        os.makedirs(to_php)

    with open(to_php/ext_data, "w") as f:
        data = f"{title}::{pod_title}::{thumb_id}"
        f.write(data)

    if not root.exists():
        os.makedirs(root)

    # Download episode.mp3 if episode.txt isn't already there
    if not (to_php/ext_txt).exists():
        with urllib.request.urlopen(link) as response, open(root/ext, 'wb') as f:
                shutil.copyfileobj(response, f)
        os.rename(root/ext, to_php/ext)

        # Start looking for episode.txt
        found_response = False
        while not found_response:
            if (to_php/ext_txt).exists():
                found_response = True
                with open(to_php/ext_txt, "r") as f:
                    ep_file_id = f.readline()
                os.remove(to_php/ext_txt)
            time.sleep(0.2)
            
    else:
        with open(to_php/ext_txt, "r") as f:
            ep_file_id = f.readline().rstrip()
        os.remove(to_php/ext_txt)

    return ep_file_id


def truncate(s):
    """
    This is called when preparing an episode for display.
    Since podcast and episode descriptions are sent as captions to the artwork,
    their length is limited to 1000 chars.

    This ensures that the provided string is shorter than 1000 chars by appropriately
    truncating everything past that threshold.
    """
    if len(s) < 1000:
        return s
    res = ''
    s_s = s.split('\n')
    i = 0
    while (len(res) < 1000) and (len(s_s[i]) < (1000 - len(res))):
        res += s_s[i] + '\n'
        i += 1
    res = res[:-1] + '…'
    
    return res


def clean_html(text):
    """
    Telegram only accepts text emphasis and link tags, so this strips the provided text
    of everything else, appropriately replacing some tags with others.
    """
    text_clean = re.sub(r'</?(p|ul|br)>|</li>', '', text)
    text_clean = re.sub(r'<(h1|h2|h3)[^>]*>', '<b>', text_clean)
    text_clean = re.sub(r'</(h1|h2|h3)>', '</b>', text_clean)
    text_clean = re.sub(r'<li>', '- ', text_clean)
    text_clean = re.sub(r'&nbsp;', ' ', text_clean)
    
    return text_clean


def convert_db_output_to_object(db_output, object_class):
    """
    A fetched row is a tuple of column values. This function converts it to a corresponding
    object
    """
    keys = POD_COLUMNS if object_class == "Pod" else EP_COLUMNS
    object_info = dict()
    for i, key in enumerate(keys):
        object_info[key] = db_output[i]

    return Pod(object_info, new=False) if object_class == "Pod" else Episode(object_info, new=False)


def convert_object_to_db_input(object):
    """
    The database expects a tuple of values corresponding to columns.
    This function generates such tuple using the object's attributes based on the object's type.
    """
    columns = POD_COLUMNS if isinstance(object, Pod) else EP_COLUMNS
    db_input = []
    for col in columns:
        db_input.append(getattr(object, col))
    
    return tuple(db_input)