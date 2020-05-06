# Global imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Local imports
from modules.tools import create_ep_index_list


def search_results_keyboard(msg_list):
    # keep max number of buttons in a row to 3
    keyboard = []
    for i, msg in enumerate(msg_list):
        keyboard.append([InlineKeyboardButton(msg,
                                    callback_data=f's_{i}')])
    
    return InlineKeyboardMarkup(keyboard)


def search_podcast_keyboard():
    keyboard = [
        [InlineKeyboardButton('Subscribe',
                              callback_data='n_i')],
        [InlineKeyboardButton('Episodes',
                              callback_data='s_p_e')]
    ]
    return InlineKeyboardMarkup(keyboard)
    

def search_episodes_keyboard(eps, s_p):
    # Returns a list of prepared keyboards for each page of
    # episode list view
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
    # IN: index of episode keyboard list for the back button
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
    keyboard = [[InlineKeyboardButton('Hide',
                              callback_data='hide')]]
    return InlineKeyboardMarkup(keyboard)
