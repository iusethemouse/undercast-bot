"""
search_logic.py

Functions that handle the search routine and podcast/episode interface.
"""

import re
import os
from telegram.ext.dispatcher import run_async

# Local imports
from . import tools
from . import inline_keyboards
from .entities import Episode

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
        pods = tools.json_to_pods(json['results'])
        keyboard = inline_keyboards.pod_list_keyboard(pods)
        update.message.reply_text(text, reply_markup=keyboard)

        # Store the podcast data for future reference.
        for pod in pods:
            if pod.pod_id not in context.bot_data:
                context.bot_data[pod.pod_id] = {"podcast": pod, "episodes_raw": None, "episodes_processed": None}


def podcast_selection_callback(update, context):
    """
    Called when a podcast is selected from any list (search results, subscriptions, etc.).

    Issues:
    - the time it takes to download and parse the RSS feed for podcasts not already stored, ~2-3 seconds.
    """
    bot = context.bot
    query = update.callback_query
    query.answer("Loading podcast...")

    pod_id = query.data
    pod = context.bot_data[pod_id]["podcast"]
    if not context.bot_data[pod_id]["episodes_processed"]:
        pod_data, episodes_data = tools.parse_feed(pod.feed_url)
        context.bot_data[pod_id]["episodes_raw"] = episodes_data
        pod.subtitle = tools.pod_subtitle_from_feed(pod_data)
        image = tools.download_artwork(pod.image_url, pod.pod_id)
    else:
        image = pod.image_file_id

    description = pod.generate_description()
    keyboard = inline_keyboards.pod_view_keyboard(pod_id)
    
    m = bot.send_photo(chat_id=update.effective_chat.id,
                   photo=open(image, 'rb') if type(image) is not str else image,
                   caption=description,
                   parse_mode='html',
                   reply_markup=keyboard)
    
    if not pod.image_file_id:
        pod.image_file_id = m.photo[0].file_id
        os.remove(image)
        context.bot_data[pod_id]["podcast"] = pod


def view_episodes_callback(update, context):
    """
    Displays a paginated list of episodes for selected podcast.

    Issues: None.
    """
    query = update.callback_query
    query.answer()

    pod_id = re.search(r'[0-9]+', query.data).group(0)
    pod = context.bot_data[pod_id]["podcast"]
    if not context.bot_data[pod_id]["episodes_processed"]:
        episodes = [Episode(ep) for ep in context.bot_data[pod_id]["episodes_raw"]]
        context.bot_data[pod_id]["episodes_processed"] = episodes
        context.bot_data[pod_id]["episodes_raw"] = None
    else:
        episodes = context.bot_data[pod_id]["episodes_processed"]
    
    keyboard_list = inline_keyboards.episodes_keyboard(episodes, pod_id)
    page_index = 0
    context.chat_data["episodes_keyboard_list"] = keyboard_list
    context.chat_data["episodes_keyboard_page_index"] = page_index
    keyboard = keyboard_list[page_index]
    
    query.edit_message_reply_markup(keyboard)
    
    
def back_to_podcast_callback(update, context):
    """
    Returns from paginated episode list view back to podcast view.

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
    page_index = context.chat_data["episodes_keyboard_page_index"] + 1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)
    

def prev_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the previous page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = context.chat_data["episodes_keyboard_page_index"] - 1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)


def last_page_of_episodes_callback(update, context):
    """
    Flips the episode list to the last page.

    Issues: None.
    """
    query = update.callback_query
    query.answer()
    
    keyboard_list = context.chat_data["episodes_keyboard_list"]
    page_index = -1
    keyboard = keyboard_list[page_index]
    context.chat_data["episodes_keyboard_page_index"] = page_index
    
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
    context.chat_data["episodes_keyboard_page_index"] = page_index
    
    query.edit_message_reply_markup(keyboard)


def episode_selection_callback(update, context):
    """
    Displays episode selected from the episode list.

    Issues:
    - Potential problems with parsing HTML of episode summaries.
    """
    query = update.callback_query
    query.answer()
    
    pod_id, ep_index = query.data.split("_")
    pod = context.bot_data[pod_id]["podcast"]
    episode = context.bot_data[pod_id]["episodes_processed"][int(ep_index)]
    page_index = context.chat_data['episodes_keyboard_page_index']
    
    description = f"<b>{pod.title}</b>\n{pod.artist}\n~\n{episode.is_chosen()}"
    keyboard = inline_keyboards.episode_view_keyboard(ep_index, pod_id, page_index, episode.too_long)
    
    query.edit_message_caption(caption=description,
                               parse_mode='html',
                               reply_markup=keyboard)
    

def view_shownotes_callback(update, context):
    """
    Sends a new message with episode show notes. This is required because of the 1000 character limit
    on photo captions, which is what podcast and episode views use.

    Issues: None.
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    pod_id, ep_index = query.data.split("shownotes")
    pod = context.bot_data[pod_id]["podcast"]
    episode = context.bot_data[pod_id]["episodes_processed"][int(ep_index)]
    
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
    # return from search episode view to eps list
    query = update.callback_query
    query.answer()
    
    pod_id, page_index = query.data.split("return_to_episode_list")
    pod = context.bot_data[pod_id]["podcast"]
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

    Issues:
    - The process is blocked while the episode is being downloaded/uploaded,
    preventing the bot from producing replies.
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    notification_msg = bot.send_message(chat_id=update.effective_chat.id,
                                        text='<i>Uploading episode, please wait…</i>',
                                        parse_mode='html')
    
    pod_id, ep_index = query.data.split("download")
    pod = context.bot_data[pod_id]["podcast"]
    ep = context.bot_data[pod_id]["episodes_processed"][int(ep_index)]

    if not ep.file_id:
        ep.file_id = ep.get_file_id(pod.title, pod.image_file_id)
        context.bot_data[pod_id]["episodes_processed"][int(ep_index)] = ep
    
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