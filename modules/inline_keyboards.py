"""
inline_keyboards.py

Inline keyboard generators that get called by logic functions.
"""


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Local imports
from .tools import create_paginated_list


def pod_list_keyboard(pods: list):
    """
    Generates a list of podcasts.
    """
    keyboard = []
    for pod in pods:
        label = f"{pod.title} | {pod.artist}"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=pod.pod_id)
            ])
    
    return InlineKeyboardMarkup(keyboard)


def pod_view_keyboard(pod_id):
    """
    Generates a keyboard for selected podcast view.
    """
    keyboard = [
        # [InlineKeyboardButton("Subscribe",
        #                       callback_data=f"subscribe{pod_id}")],
        [InlineKeyboardButton("Episodes",
                              callback_data=f"episodes{pod_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)
    

def episodes_keyboard(eps, pod_id):
    """
    Returns a list of prepared keyboards for each page of episode list view.
    """
    max_eps_per_page = 6
    idx_list = create_paginated_list(max_eps_per_page, len(eps))
    keyboards= []
    first_page = InlineKeyboardButton("<< First", callback_data="episodes_first_page")
    last_page = InlineKeyboardButton("Last >>", callback_data="episodes_last_page")
    prev_page = InlineKeyboardButton("< Prev", callback_data="episodes_prev_page")
    next_page = InlineKeyboardButton("Next >", callback_data="episodes_next_page")
    back_to_pod = InlineKeyboardButton("Back to podcast", callback_data=f"return{pod_id}")
    
    start = 0
    for page_index in range(len(idx_list)):
        keyboard = []
        end = idx_list[page_index]
        for ep_index in range(start, end):
            ep = eps[ep_index]
            keyboard.append([InlineKeyboardButton(f'{ep.title} | {ep.duration}',
                            callback_data=f'{pod_id}_{ep.ep_id}')])
        # add prev, next, and back to podcast buttons to k
        if (page_index == 0) and (page_index != len(idx_list) - 1):
            keyboard.append([next_page, last_page])
        elif (page_index == len(idx_list) - 1) and (page_index != 0):
            keyboard.append([first_page, prev_page])
        elif page_index != 0:
            keyboard.append([first_page, prev_page, next_page, last_page])
        keyboard.append([back_to_pod])
        start = end
            
        keyboards.append(InlineKeyboardMarkup(keyboard))

    return keyboards


def episode_view_keyboard(ep_id, pod_id, page_index, too_long):
    """
    Keyboard for individual episode view.
    """
    too_long = bool(int(too_long)) # convert the potentially 0/1 value returned by the database
    keyboard = [[InlineKeyboardButton('View show notes', callback_data=f"{pod_id}shownotes{ep_id}")]] if too_long else []
    
    keyboard.append([InlineKeyboardButton('Download', callback_data=f"{pod_id}download{ep_id}")])
    keyboard.append([InlineKeyboardButton('Back to episode list', callback_data=f"{pod_id}return_to_episode_list{page_index}")])
        
    return InlineKeyboardMarkup(keyboard)


def hide_shownotes_keyboard():
    """
    A single button for the show notes view.
    """
    keyboard = [[InlineKeyboardButton('Hide', callback_data='hide_shownotes')]]
    return InlineKeyboardMarkup(keyboard)
