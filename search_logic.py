# Global imports
import re
import os

# Local imports
import tools
import inline_keyboards
from action_wrappers import send_typing_action

def search(update, context):
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
    bot = context.bot
    query = update.callback_query
    query.answer()
    idx = int(re.search(r'[0-9]', query.data).group(0))
    
    pod = context.chat_data['pod_list'][idx]
    if pod.collection_id in context.bot_data['podcasts']:
        pod = context.bot_data['podcasts'][pod.collection_id]
        img_f_id = pod.image_file_id
    else:
        img_path = pod.get_image_path()
        pod.get_eps_and_subs()
    
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
    query = update.callback_query
    query.answer()
    
    query.edit_message_reply_markup(inline_keyboards.search_podcast_keyboard())
    
    
def s_p_e_next_button(update, context):
    query = update.callback_query
    query.answer()
    
    k_list = context.chat_data['s_p_e_k_list']
    idx = context.chat_data['s_p_e_k_idx'] + 1
    k = k_list[idx]
    context.chat_data['s_p_e_k_idx'] = idx
    
    query.edit_message_reply_markup(k)
    

def s_p_e_prev_button(update, context):
    query = update.callback_query
    query.answer()
    
    k_list = context.chat_data['s_p_e_k_list']
    idx = context.chat_data['s_p_e_k_idx'] - 1
    k = k_list[idx]
    context.chat_data['s_p_e_k_idx'] = idx
    
    query.edit_message_reply_markup(k)

    
def s_pod_eps_ep_button(update, context):
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
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.delete_message(chat_id=update.effective_chat.id,
                      message_id=query.message.message_id)
    

def s_p_e_e_to_e_button(update, context):
    # return from search episode view to eps list
    query = update.callback_query
    query.answer()
    
    k_l_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    k = context.chat_data['s_p_e_k_list'][k_l_idx]
    
    query.edit_message_caption(caption=pod.is_chosen(),
                              parse_mode='html',
                              reply_markup=k)
    

def s_e_download_button(update, context):
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    note_msg = bot.send_message(chat_id=update.effective_chat.id,
                   text='<i>Downloading episode, please wait…</i>',
                   parse_mode='html')
    
    ep_idx = int(re.search(r'[0-9]+', query.data).group(0))
    pod = context.chat_data['s_p']
    ep = pod.episodes[ep_idx]
    parts = 0
    f_id_mode = True
    if ep.hash in context.bot_data['episodes']:
        ep = context.bot_data['episodes'][ep.hash]
        file_ids = ep.file_ids
        parts = len(file_ids)
    else:
        file_paths = ep.get_file_paths()
        parts = len(file_paths)
        f_id_mode = False
        
    bot.edit_message_text(chat_id=update.effective_chat.id,
                      message_id=note_msg.message_id,
                      text='<i>Uploading episode, please wait…</i>',
                      parse_mode='html')
    
    msg = f"<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{ep.title}</b>\n{ep.duration} <b>·</b> {ep.published_str}\n\nvia @undercast_bot"

    messages = []
    
    if parts == 1:
        m = bot.send_audio(chat_id=update.effective_chat.id,
                       audio=open(file_paths[0], 'rb') if not f_id_mode else file_ids[0],
                       performer=pod.title,
                       title=ep.title,
                       thumb=pod.image_file_id,
                       caption=msg,
                       parse_mode='html',
                       timeout=120)
        messages.append(m)
    else:
        file_items = file_paths if not f_id_mode else file_ids
        for i, file in enumerate(file_items):
            part_msg = f"Part {i+1} of {len(file_items)}\n<b>{pod.title}</b>\n<i>{pod.artist}</i>\n~\n<b>{ep.title}</b>\n" \
                        f"{ep.duration} <b>·</b> {ep.published_str}\n\nvia @undercast_bot"
            
            m = bot.send_audio(chat_id=update.effective_chat.id,
                       audio=open(file, 'rb') if not f_id_mode else file,
                       performer=pod.title,
                       title=f"Pt. {i+1}, "+ep.title,
                       thumb=pod.image_file_id,
                       caption=part_msg,
                       parse_mode='html',
                          timeout=120)
            messages.append(m)
            
    bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=note_msg.message_id)
    
    if not f_id_mode:
        ids = [mes.audio.file_id for mes in messages]
        ep.file_ids = ids
        context.bot_data['episodes'][ep.hash] = ep
        
        for p in file_paths:
            os.remove(p)