"""
search_logic.py

Functions that handle the search routine and podcast/episode interface.

Interfacing between Pod/Episode objects and the database:
- tools.convert_db_output_to_object(db_output, object_class)
- tools.convert_object_to_db_input(object)
"""

import re, os
from telegram.ext.dispatcher import run_async

# Local imports
from . import tools, inline_keyboards
from .database import db
from .entities import Pod, Episode

def search(update, context):
    """
    Any plaintext message is considered a search query.
    """
    search_term = '+'.join(update.message.text.split(' '))
    json = tools.get_search_json(search_term)
    n = json['resultCount']
    if n == 0:
        update.message.reply_text("Couldn't find anything, try a different search term.")
    else:
        text = f"Found {n} result" + ("s:" if n > 1 else ":")
        pods = tools.json_to_pods(json['results']) # a list of Pod objects
        keyboard = inline_keyboards.pod_list_keyboard(pods)
        update.message.reply_text(text, reply_markup=keyboard)

        # Store the podcast data for future reference.
        for pod in pods:
            if not db.get_podcast(pod.pod_id):
                pod_data = tools.convert_object_to_db_input(pod)
                db.add_podcast(pod_data)
            else:
                print(f"{pod.title} already in podcast table.")


def podcast_selection_callback(update, context):
    """
    Called when a podcast is selected from any list (search results, subscriptions, etc.).

    Issues:
    - Takes too long to download and parse the RSS feed for podcasts not already stored, ~2-3 seconds.
    """
    bot = context.bot
    query = update.callback_query
    query.answer("Loading podcast...")

    pod_id = query.data
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod") # this is a Pod object

    if not db.episodes_are_stored(pod.pod_id):
        feed_info, episodes_raw = tools.parse_feed(pod.feed_url)
        episodes = [Episode(ep, pod.pod_id, index) for index, ep in enumerate(episodes_raw)]
        for ep in episodes:
            ep_data = tools.convert_object_to_db_input(ep)
            db.add_episode(ep_data)
        pod.subtitle = tools.get_pod_subtitle_from_feed(feed_info)
        image = tools.download_artwork(pod.image_url, pod.pod_id)
    else:
        image = pod.image_file_id

    description = pod.generate_description()
    keyboard = inline_keyboards.pod_view_keyboard(pod.pod_id)
    
    m = bot.send_photo(chat_id=update.effective_chat.id,
                   photo=open(image, 'rb') if type(image) is not str else image,
                   caption=description,
                   parse_mode='html',
                   reply_markup=keyboard)
    
    # store artwork file ID and subtitle in db
    if type(image) is not str:
        pod.image_file_id = str(m.photo[0].file_id)
        columns_to_update = {
            "image_file_id": pod.image_file_id,
            "subtitle": pod.subtitle
            }
        db.update_item_in_table(pod.pod_id, "podcasts", columns_to_update)

        os.remove(image)


def view_episodes_callback(update, context):
    """
    Displays a paginated list of episodes for selected podcast.

    Issues: None.
    """
    query = update.callback_query
    query.answer()

    pod_id = re.search(r'[0-9]+', query.data).group(0)
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod")

    episodes_raw = db.get_all_episodes(pod.pod_id)
    episodes = [tools.convert_db_output_to_object(ep, "Episode") for ep in episodes_raw] # a list of Episode objects
    
    keyboard_list = inline_keyboards.episodes_keyboard(episodes, pod.pod_id)

    page_index = 0
    context.chat_data["episodes_keyboard_list"] = keyboard_list
    context.chat_data["episodes_keyboard_list_page_index"] = page_index
    keyboard = keyboard_list[page_index]
    
    query.edit_message_reply_markup(keyboard)
    
    
def back_to_podcast_callback(update, context):
    """
    Returns back to podcast view from any other view related to the podcast.

    Issues: None.
    """
    query = update.callback_query
    query.answer()

    pod_id = re.search(r'[0-9]+', query.data).group(0)
    keyboard = inline_keyboards.pod_view_keyboard(pod_id)
    
    query.edit_message_reply_markup(keyboard)
    
    
def next_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the next page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()

    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = context.chat_data["episodes_keyboard_list_page_index"] + 1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_list_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)
    

def prev_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the previous page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = context.chat_data["episodes_keyboard_list_page_index"] - 1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_list_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)


def last_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the last page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = len(keyboard_list) - 1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_list_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)


def first_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the first page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = 0
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_list_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)


def episode_selection_callback(update, context):
    """
    Displays episode selected from the episode list.

    Issues:
    - None.
    """
    query = update.callback_query
    query.answer()
    
    pod_id, ep_id = query.data.split("_")
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod")
    episode = tools.convert_db_output_to_object(db.get_episode(ep_id), "Episode")

    ep_had_shownotes = episode.shownotes != ""

    page_index = context.chat_data['episodes_keyboard_list_page_index']
    description = f"<b>{pod.title}</b>\n{pod.artist}\n~\n{episode.is_chosen()}"
    keyboard = inline_keyboards.episode_view_keyboard(ep_id, pod_id, page_index, episode.too_long)
    
    query.edit_message_caption(caption=description,
                               parse_mode='html',
                               reply_markup=keyboard)

    if not ep_had_shownotes:
        columns_to_update = {
            "shownotes": episode.shownotes
        }
        db.update_item_in_table(episode.ep_id, "episodes", columns_to_update)
    

def view_shownotes_callback(update, context):
    """
    Sends a new message with episode show notes. This is required because of the 1000 character limit
    on photo captions, which is what podcast and episode views use.

    Issues: None.
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    pod_id, ep_id = query.data.split("shownotes")
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod")
    episode = tools.convert_db_output_to_object(db.get_episode(ep_id), "Episode")
    
    text = f"<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{episode.title}</b>\n\n{episode.shownotes}"
    keyboard = inline_keyboards.hide_shownotes_keyboard()
    bot.send_message(chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode='html',
                    reply_markup=keyboard)

    
def hide_shownotes_callback(update, context):
    """
    Deletes the show notes message.

    Issues: None.
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.delete_message(chat_id=update.effective_chat.id,
                      message_id=query.message.message_id)
    

def return_to_episode_list_callback(update, context):
    """
    Returns back to the episode list view preserving the page position.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    pod_id, page_index = query.data.split("return_to_episode_list")
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod")
    text = pod.generate_description()
    keyboard = context.chat_data["episodes_keyboard_list"][int(page_index)]
    
    query.edit_message_caption(caption=text,
                              parse_mode='html',
                              reply_markup=keyboard)
    

@run_async
def download_episode_callback(update, context):
    """
    Sends a new message with the audio file of the episode.
    Always uses Telegram's fileID via start_file_uploader.php
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    notification_msg = bot.send_message(chat_id=update.effective_chat.id,
                                        text='<i>Uploading episode, please wait…</i>',
                                        parse_mode='html')
    
    pod_id, ep_id = query.data.split("download")
    pod = tools.convert_db_output_to_object(db.get_podcast(pod_id), "Pod")
    ep = tools.convert_db_output_to_object(db.get_episode(ep_id), "Episode")

    if not ep.file_id:
        ep.file_id = ep.get_file_id(pod.title, pod.image_file_id)
        columns_to_update = {
            "file_id": ep.file_id
        }
        db.update_item_in_table(ep.ep_id, "episodes", columns_to_update)
    
    text = f"<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{ep.title}</b>\n{ep.duration} <b>·</b> {ep.published_str}\n\nvia @undercast_bot"
    bot.send_audio(chat_id=update.effective_chat.id,
                    audio=ep.file_id,
                    performer=pod.title,
                    title=ep.title,
                    caption=text,
                    parse_mode='html',
                    timeout=120)
            
    bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=notification_msg.message_id)