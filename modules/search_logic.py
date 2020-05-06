"""Logic for the search routine.

The routine is initiated with the /search command. After that,
all communication between functions is through callback queries
from inline buttons.

/search term -> search result list -> selected podcast <-> episode list <-> selected episode

TODO: generalise some of the functions to work with other routines (i.e. subscriptions)

"""

# Global imports
import re
import os

# Local imports
import modules.tools as tools
import modules.inline_keyboards as inline_keyboards
from modules.action_wrappers import send_typing_action

def search(update, context):
    """
    Initiates the routine.

    User is sent a message with an inline button for each podcast in
    the search result.
    """

    if len(context.args) == 0:
        msg_header, msg_body = 'Usage: /search search-term', []
    else:
        search_term = '+'.join(context.args)
        json = tools.get_search_json(search_term)
        msg_list, keys, pod_list = tools.json_to_msg_keys_pod_list(json)
        if keys != []:
            msg_header, msg_body = msg_list[0], msg_list[1:]   
            context.chat_data['pod_list'] = pod_list
        else:
            msg_header, msg_body = msg_list, []
        
        
    update.message.reply_text(msg_header,
                              reply_markup=inline_keyboards.search_results_keyboard(msg_body))


@send_typing_action
def s_pod_button(update, context):
    """
    s_pod_button: Search Podcast Button

    Sends the user an image message with the selected podcast information
    as image caption, parsed as HTML.

    Inline buttons include "Subscribe" and "Episodes"

    """

    bot = context.bot
    query = update.callback_query
    query.answer()
    idx = int(re.search(r'[0-9]', query.data).group(0))
    
    pod = context.chat_data['pod_list'][idx]

    # Check for file ID for podcast artwork image
    if pod.collection_id in context.bot_data['podcasts']:
        pod = context.bot_data['podcasts'][pod.collection_id]
        img_f_id = pod.image_file_id
    else:
        img_path = pod.get_image_path()
        pod.get_eps_and_subs()
    
    # Loads podcast subtitle and processes all episodes
    msg = pod.is_chosen()
    
    m = bot.send_photo(chat_id=update.effective_chat.id,
                   photo=open(img_path, 'rb') if not pod.image_file_id else img_f_id,
                   caption=msg,
                   parse_mode='html',
                   reply_markup=inline_keyboards.search_podcast_keyboard())
    
    if not pod.image_file_id:
        pod.image_file_id = m.photo[0].file_id
        context.bot_data['podcasts'][pod.collection_id] = pod
    
    context.chat_data['s_p'] = pod
    context.chat_data['s_p_idx'] = query.data


def s_pod_eps_button(update, context):
    """
    s_pod_eps_button: Search Podcast Episodes Button

    Activated when user selects to view episodes of selected
    podcast. Selected podcast message is edited to have the paginated
    list of episodes as inline buttons.
    """

    query = update.callback_query
    query.answer()
    
    pod = context.chat_data['s_p']
    s_p = context.chat_data['s_p_idx'] + '_r'
    
    eps = pod.episodes
    k_list = inline_keyboards.search_episodes_keyboard(eps, s_p)
    idx = 0
    context.chat_data['s_p_e_k_list'] = k_list
    context.chat_data['s_p_e_k_idx'] = idx
    k = k_list[idx]
    
    query.edit_message_reply_markup(k)
    
    
def s_eps_to_pod_button(update, context):
    """
    s_eps_to_pod_button: Search Episodes to Podcast Button

    Activated when the user chooses to return to the selected podcast
    view from the episode list view.

    The podcast message is edited to have the "Subscribe" and "Episodes" inline
    buttons.
    """

    query = update.callback_query
    query.answer()
    
    query.edit_message_reply_markup(inline_keyboards.search_podcast_keyboard())
    
    
def s_p_e_next_button(update, context):
    """
    s_p_e_next_button: Search Podcast Episode Next Button

    Activated when the user wants to go to the next page of the
    episode list for selected podcast. The page number of the
    episode list keyboard is incremented and the keyboard is regenerated.
    """

    query = update.callback_query
    query.answer()
    
    k_list = context.chat_data['s_p_e_k_list']
    idx = context.chat_data['s_p_e_k_idx'] + 1
    k = k_list[idx]
    context.chat_data['s_p_e_k_idx'] = idx
    
    query.edit_message_reply_markup(k)
    

def s_p_e_prev_button(update, context):
    """
    s_p_e_prev_button: Search Podcast Episode Previous Button

    Activated when the user wants to go to the previous page of the
    episode list for selected podcast. The page number of the
    episode list keyboard is decremented and the keyboard is regenerated.
    """

    query = update.callback_query
    query.answer()
    
    k_list = context.chat_data['s_p_e_k_list']
    idx = context.chat_data['s_p_e_k_idx'] - 1
    k = k_list[idx]
    context.chat_data['s_p_e_k_idx'] = idx
    
    query.edit_message_reply_markup(k)

    
def s_pod_eps_ep_button(update, context):
    """
    s_pod_eps_ep_button: Search Podcast Episodes Episode Button

    Activated when an episode is selected from the episode list for
    selected podcast. The podcast message is edited to have a new
    set of inline buttons: "Download", "Back to episode list", and,
    optionally, "View show notes" if episode has them.

    TODO: Certain show notes have a parsing problem with <img> and <br> tags.
    """

    query = update.callback_query
    query.answer()
    
    ep_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    k_l_idx = context.chat_data['s_p_e_k_idx']
    ep = pod.episodes[ep_idx]
    
    msg = f"<b>{pod.title}</b>\n{pod.artist}\n~\n{ep.is_chosen()}"
    k = inline_keyboards.search_chosen_episode_keyboard(ep_idx, k_l_idx, ep.too_long)
    
    query.edit_message_caption(caption=msg,
                              parse_mode='html',
                              reply_markup=k)
    

def s_p_e_subt_button(update, context):
    """
    s_p_e_subt_button: Search Podcast Episode Subtitle Button

    Activated when the "View show notes" button is actioned.
    Sends a new message with full show notes parsed as HTML, as text messages
    have no character limit as opposed to image caption (which the podcast message
    utilises for displaying podcast and episode descriptions).
    """

    bot = context.bot
    query = update.callback_query
    query.answer()
    
    ep_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    ep = pod.episodes[ep_idx]
    
    msg = f"<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{ep.title}</b>\n\n{ep.shownotes}"
    bot.send_message(chat_id=update.effective_chat.id,
                         text=msg,
                         parse_mode='html',
                         reply_markup=inline_keyboards.hide_shownotes_keyboard())
    

def s_p_e_hide_sub_button(update, context):
    """
    s_p_e_hide_sub_button: Search Podcast Episode Hide Subtitle Button

    Activated when the user chooses to hide the show notes message.
    The message is deleted.
    """

    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.delete_message(chat_id=update.effective_chat.id,
                      message_id=query.message.message_id)
    

def s_p_e_e_to_e_button(update, context):
    """
    s_p_e_e_to_e_button: Search Podcast Episodes Episode to Episodes Button

    Activated when the user wants to return from the selected episode back to
    the list of episodes. The page number is conserved.
    """

    query = update.callback_query
    query.answer()
    
    k_l_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    k = context.chat_data['s_p_e_k_list'][k_l_idx]
    
    query.edit_message_caption(caption=pod.is_chosen(),
                              parse_mode='html',
                              reply_markup=k)
    

def s_e_download_button(update, context):
    """
    s_e_download_button: Search Episode Download Button

    Activated when the user wants to download the selected episode.

    The file ID is sent if the episode has already been downloaded before by
    any user, alternatively a request is sent to the secondary process, which uploads
    the episode to Telegram's servers and returns its file ID to the primary process.

    A message is then sent with the audio file (title: episode title, artist: podcast name)
    with a short display message for context. The message is then shareable, the audio file
    is downloadable.

    TODO: Improve feedback to the user indicating what stage (downloading/uploading) the
    process is currently at. Implement the process in an async way to remove the blocking
    nature of the current implementation.
    """

    bot = context.bot
    query = update.callback_query
    query.answer()
    
    note_msg = bot.send_message(chat_id=update.effective_chat.id,
                   text='<i>Downloading episode, please wait…</i>',
                   parse_mode='html')
    
    ep_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    ep = pod.episodes[ep_idx]
    
    if ep.hash in context.bot_data['episodes']:
        ep = context.bot_data['episodes'][ep.hash]
        file_id = ep.file_id
    else:
        file_id = ep.get_file_id(pod.title, pod.image_file_id)
        context.bot_data['episodes'][ep.hash] = ep
        
    bot.edit_message_text(chat_id=update.effective_chat.id,
                      message_id=note_msg.message_id,
                      text='<i>Uploading episode, please wait…</i>',
                      parse_mode='html')
    
    msg = f"<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{ep.title}</b>\n{ep.duration} <b>·</b> {ep.published_str}\n\nvia @undercast_bot"
    bot.send_audio(chat_id=update.effective_chat.id,
                    audio=file_id,
                    performer=pod.title,
                    title=ep.title,
                    thumb=pod.image_file_id,
                    caption=msg,
                    parse_mode='html',
                    timeout=120)
            
    bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=note_msg.message_id)