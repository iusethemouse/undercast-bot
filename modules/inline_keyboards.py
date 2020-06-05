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


def pod_view_keyboard(pod_id, user_id, is_subscribed):
    """
    Generates a keyboard for selected podcast view.
    """
    if is_subscribed:
        keyboard = [
            [InlineKeyboardButton("Unsubscribe", callback_data=f"{pod_id}unsubscribe{user_id}")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Subscribe", callback_data=f"{pod_id}subscribe{user_id}")]
        ]
    keyboard.append([InlineKeyboardButton("Episodes", callback_data=f"episodes{pod_id}")])
    
    return InlineKeyboardMarkup(keyboard)
    

def episodes_keyboard(eps, pod_id, user_id):
    """
    Returns a list of prepared keyboards for each page of episode list view.
    """
    max_eps_per_page = 6
    idx_list = create_paginated_list(max_eps_per_page, len(eps))
    keyboards= []
    first_page = InlineKeyboardButton("<< First", callback_data="eps_navigation_first")
    last_page = InlineKeyboardButton("Last >>", callback_data="eps_navigation_last")
    prev_page = InlineKeyboardButton("< Prev", callback_data="eps_navigation_prev")
    next_page = InlineKeyboardButton("Next >", callback_data="eps_navigation_next")
    back_to_pod = InlineKeyboardButton("Back to podcast", callback_data=f"{pod_id}return{user_id}")
    
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


def subscriptions_keyboard(pods):
    """
    Returns a list of prepared keyboards for each page of subscription list view.
    """
    max_pods_per_page = 7
    idx_list = create_paginated_list(max_pods_per_page, len(pods))
    keyboards= []
    first_page = InlineKeyboardButton("<< First", callback_data="subs_navigation_first")
    last_page = InlineKeyboardButton("Last >>", callback_data="subs_navigation_last")
    prev_page = InlineKeyboardButton("< Prev", callback_data="subs_navigation_prev")
    next_page = InlineKeyboardButton("Next >", callback_data="subs_navigation_next")
    
    start = 0
    for page_index in range(len(idx_list)):
        keyboard = []
        end = idx_list[page_index]
        for pod_index in range(start, end):
            pod = pods[pod_index]
            keyboard.append([InlineKeyboardButton(f"{pod.title} | {pod.artist}",
                            callback_data=pod.pod_id)])
        # add navigation buttons to keyboard
        if (page_index == 0) and (page_index != len(idx_list) - 1):
            keyboard.append([next_page, last_page])
        elif (page_index == len(idx_list) - 1) and (page_index != 0):
            keyboard.append([first_page, prev_page])
        elif page_index != 0:
            keyboard.append([first_page, prev_page, next_page, last_page])
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
