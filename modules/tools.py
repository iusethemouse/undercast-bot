# General modules
import requests
import re
import feedparser
from pathlib import Path
import os
from hashlib import sha1
from datetime import datetime, timedelta
from math import fabs
import urllib.request
import shutil
#from pydub import AudioSegment
import time

# Local modules
from modules.entities import Pod, Episode

# Globals
IMG_ROOT = Path('artwork/')
EP_ROOT = Path('episodes/')
PHP_ROOT = Path('episode_uploader/episodes_to_send/')
MAX_SEARCH_RESULTS = 6


def get_search_json(search_term):
    # IN: search string with '+'s instead of spaces
    # OUT: iTunes response in a json-like dict;
    max_results = str(MAX_SEARCH_RESULTS)
    itunes_url = "https://itunes.apple.com/search?&media=podcast&limit="+max_results+"&term="
    search_url = itunes_url + search_term
    json_result = requests.get(search_url).json()
    
    return json_result


def json_to_msg_keys_pod_list(json_result):
    n = json_result['resultCount']
    if n == 0:
        msg = "Couldn't find anything. Try another search term."
        keys, pod_list = [], []
    else:
        pod_list = json_to_pod_list(json_result)
        msg = pod_list_to_msg_list(pod_list)
        keys = pod_list_to_keys(pod_list)

    return msg, keys, pod_list


def json_to_pod_list(json):
    # generate a list of Pod objects from search result json
    pod_list = []
    for pod in json['results']:
        pod = Pod(pod)
        if pod.valid:
            pod_list.append(pod)
    
    return pod_list


def pod_list_to_keys(pod_list):
    return [i+1 for i in range(len(pod_list))]


def pod_list_to_msg_list(pod_list):
    # pods are Pod objects
    msg_list = [f"Found {len(pod_list)} result(s):"]
    for pod in pod_list:
        msg_list.append(pod.to_msg_list())
    
    return msg_list


def date_to_txt(date_str):
    # Provide date estimates for latest episodes
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


def get_pod_image_path(img_url, col_id):
    # Used by .get_image_path method of Pod class
    # see global variable IMG_ROOT to specify destination for images
    ext = col_id + '.jpeg'
    root = IMG_ROOT
    
    if not root.exists():
        os.makedirs(IMG_ROOT)
    if not (root/ext).exists():
        img_data = requests.get(img_url)
        with open(root/ext, 'wb') as im_file:
            im_file.write(img_data.content)
    
    return root/ext


def get_pod_subtitle_from_feed(feed_url):
    # Used to retrieve subtitle for a Pod object
    feed = feedparser.parse(feed_url)
    try:
        text = feed['feed']['summary']
        if len(feed['feed']['subtitle']) != 0:
            text = feed['feed']['subtitle']
    except KeyError:
        text = feed['feed']['subtitle']
        
    return clean_html(text)


def get_ep_sub_sum(ep_info):
    s = ['',''] # sub and sum
    if 'subtitle' in ep_info:
        s[0] = ep_info['subtitle']
        
    s[1] = ep_info['summary']
        
    for i in range(2):
        s[i] = clean_html(s[i])
        
    return s[0], s[1]


def get_ep_duration(ep):
    # returns duration as string of either formats:
    # Xh Ym or Zm
    s = '-'
    if 'itunes_duration' in ep:
        dur = ep['itunes_duration']
        if ':' not in dur:
            dur = str(timedelta(seconds=int(dur)))
        t = re.sub(r'^0{1,2}:*|(?<=:)0', '', dur[:-3])
        s = re.sub(r':', 'h ', t) + 'm'
    
    return s


def get_ep_source_link(link_list):
    for link_dict in link_list:
        if '.mp3' in link_dict['href']:
            return link_dict['href']
    

def get_ep_list_from_feed(feed_url):
    feed = process_pod_feed(feed_url)
    eps = feed['entries']
    
    return [Episode(ep) for ep in eps]


def process_pod_feed(feed_url):
    return feedparser.parse(feed_url)


def hash_ep_title(t):
    return sha1(t.encode('UTF-8')).hexdigest()


def process_ep_date(date_str):
    try:
        res = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        res = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %Z")
        
    return res


def create_ep_index_list(res_size, n_eps):
    n_chunks = n_eps // res_size
    res_list = [res_size * i for i in range(1, n_chunks + 1)]
    remainder = n_eps - res_size * n_chunks
    
    if remainder != 0:
        res_list.append(n_eps)
        
    return res_list


def create_file_index_list(max_size, f_len):
    n_chunks = f_len // max_size
    res_list = [max_size * i for i in range(1, n_chunks + 1)]
    remainder = f_len - max_size * n_chunks
    
    if remainder != 0:
        res_list.append(f_len)
        
    return res_list


def download_ep(link, title, podcast, thumb_id):
    # Download episode episode.mp3;
    # Start looking for episode.txt, which will contain the file_id from MadelineProto;
    # Return the episode file_id.
    root = EP_ROOT
    to_php = PHP_ROOT
    name = re.sub(r"\W", '_', title)
    ext = name + '.mp3'
    ext_txt = name + '.txt'
    ext_data = name + '_data.txt'

    if not root.exists():
        os.makedirs(root)
    if not to_php.exists():
        os.makedirs(to_php)

    with open(to_php/ext_data, "w") as f:
        data = f"{title}::{podcast}::{thumb_id}"
        f.write(data)

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


# def split_audio_file(ratio, root, name):
#     # returns a list of paths for file parts
#     parts = []
#     ep = AudioSegment.from_mp3(root/(name+'.mp3'))
#     ep_size = len(ep)
#     max_size = int(ep_size / ratio)
#     idx_list = create_file_index_list(max_size, ep_size)
    
#     start = 0
#     for i in range(len(idx_list)):
#         end = idx_list[i]
#         ep_part = ep[start:end]
#         part_path = root/(name + f"_Part_{i+1}.mp3")
#         ep_part.export(part_path, format='mp3')
#         parts.append(part_path)
#         start = end
    
#     return parts


def truncate(s):
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
    text_new = re.sub(r'</?(p|h2|ul|br)>|</li>', '', text)
    text_new = re.sub(r'<li>', '\n- ', text_new)
    text_new = re.sub(r'&nbsp;', ' ', text_new)
    
    return text_new