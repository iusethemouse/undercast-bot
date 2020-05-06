"""Generators of inline keyboards for various routines.

TODO: Generalise some keyboards to be applicable to requests
from future routines (i.e. subscriptions).

"""

# Global imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Local imports
from modules.tools import create_ep_index_list

def search_results_keyboard(msg_list: list):
    """
    Generates a list of inline buttons with a podcast display
    message as label.

    Each button sends a callback query with the podcast's index
    in the searh result list, or pod_list.
    """

    keyboard = []
    for i, msg in enumerate(msg_list):
        keyboard.append([InlineKeyboardButton(msg,
                                    callback_data=f's_{i}')])
    
    return InlineKeyboardMarkup(keyboard)


def search_podcast_keyboard():
    """
    Generates a keyboard for the podcast selected from search result
    list.
    
    Currently 'Subscribe' leads to a "not implemented" message.
    """

    keyboard = [
        [InlineKeyboardButton('Subscribe',
                              callback_data='n_i')],
        [InlineKeyboardButton('Episodes',
                              callback_data='s_p_e')]
    ]

    return InlineKeyboardMarkup(keyboard)
    

def search_episodes_keyboard(eps, s_p):
    """
    Generates a list of pages of episodes for selected podcast.
    Either all episodes fit onto one page of size max_eps_per_page,
    or multiple pages are generated.

    Each button has label "Episode Title | Episode Duration".

    TODO: add 'first' and 'last' buttons to navigate to the first
    and last pages of the list respectively. Useful when there are hundreds
    of episodes.
    """

    max_eps_per_page = 6
    idx_list = create_ep_index_list(max_eps_per_page, len(eps))
    keyboards= []
    prev_b = InlineKeyboardButton('<< Prev. page', callback_data='s_p_e_prev')
    next_b = InlineKeyboardButton('Next page >>', callback_data='s_p_e_next')
    back_b = InlineKeyboardButton('Back to podcast', callback_data=s_p)
    
    if len(idx_list) == 1:    # episodes fit into one list view
        k = []
        for i in range(idx_list[0]):
            ep = eps[i]
            t = ep.title
            d = ep.duration
            k.append([InlineKeyboardButton(f'{t} | {d}',
                              callback_data=f's_p_e_e_{i}')])
        k.append([InlineKeyboardButton('Back to podcast',
                              callback_data=s_p)])
        keyboards.append(InlineKeyboardMarkup(k))
    else:
        start = 0
        for i in range(len(idx_list)):
            k = []
            end = idx_list[i]
            for j in range(start, end):
                ep = eps[j]
                t = ep.title
                d = ep.duration
                k.append([InlineKeyboardButton(f'{t} | {d}',
                              callback_data=f's_p_e_e_{j}')])
            # add prev, next, and back to podcast buttons to k
            if i == 0:
                k.append([next_b]) 
            elif i == len(idx_list) - 1:
                k.append([prev_b])
            else:
                k.append([prev_b, next_b])
            k.append([back_b])
            start = end
                
            keyboards.append(InlineKeyboardMarkup(k))

    return keyboards


def search_chosen_episode_keyboard(ep_idx, k_l_idx, too_long):
    """
    Generates inline buttons the episode selected from the episode
    list view. When returning back to the episode list, the page number
    is conserved.

    Optionally, the "View show notes" button is displayed if Episode.too_long
    is True.
    """

    keyboard = [
        [InlineKeyboardButton('Download',
                              callback_data=f's_e_down_{ep_idx}')],
        [InlineKeyboardButton('Back to episode list',
                              callback_data=f's_p_e_{k_l_idx}')]
    ]
    
    if too_long:
        keyboard.insert(0, [InlineKeyboardButton('View show notes',
                              callback_data=f's_e_subt_{ep_idx}')])
        
    return InlineKeyboardMarkup(keyboard)


def hide_shownotes_keyboard():
    """
    Generates a single inline button to delete the show notes
    message for selected episode.
    """

    keyboard = [[InlineKeyboardButton('Hide',
                              callback_data='hide')]]
                              
    return InlineKeyboardMarkup(keyboard)
