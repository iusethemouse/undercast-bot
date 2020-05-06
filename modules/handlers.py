# Global imports
from telegram.ext import (CommandHandler, 
                          MessageHandler, 
                          CallbackQueryHandler,
                          Filters)

# Local imports
import modules.search_logic as search_logic
import modules.generic_logic as generic_logic


# Search handlers
search_handler = CommandHandler('search', search_logic.search)
s_pod_button_handler = CallbackQueryHandler(search_logic.s_pod_button, pattern='^s_[0-9]$')
s_pod_eps_button_handler = CallbackQueryHandler(search_logic.s_pod_eps_button, pattern='^s_p_e$')
s_pod_eps_ep_button_handler = CallbackQueryHandler(search_logic.s_pod_eps_ep_button, pattern='^s_p_e_e_[0-9]+$')
s_eps_to_pod_button_handler = CallbackQueryHandler(search_logic.s_eps_to_pod_button, pattern='^s_[0-9]_r$')
s_p_e_next_button_handler = CallbackQueryHandler(search_logic.s_p_e_next_button, pattern='^s_p_e_next$')
s_p_e_prev_button_handler = CallbackQueryHandler(search_logic.s_p_e_prev_button, pattern='^s_p_e_prev$')
s_p_e_e_to_e_button_handler = CallbackQueryHandler(search_logic.s_p_e_e_to_e_button, pattern='^s_p_e_[0-9]+$')
s_e_download_button_handler = CallbackQueryHandler(search_logic.s_e_download_button, pattern='^s_e_down_[0-9]+$')
s_p_e_subt_button_handler = CallbackQueryHandler(search_logic.s_p_e_subt_button, pattern='^s_e_subt_[0-9]+$')
s_p_e_hide_sub_button_handler = CallbackQueryHandler(search_logic.s_p_e_hide_sub_button, pattern='^hide$')

# Generic handlers
start_handler = CommandHandler('start', generic_logic.start)
not_imp_handler = CallbackQueryHandler(generic_logic.not_imp_button, pattern='^n_i$')
echo_handler = MessageHandler(Filters.text & (~Filters.command), generic_logic.echo)
unknown_handler = MessageHandler(Filters.command, generic_logic.unknown)

handlers = [search_handler,
        s_pod_button_handler,
        s_pod_eps_button_handler,
        s_pod_eps_ep_button_handler,
        s_eps_to_pod_button_handler,
        s_p_e_next_button_handler,
        s_p_e_prev_button_handler,
        s_p_e_e_to_e_button_handler,
        s_e_download_button_handler,
        s_p_e_subt_button_handler,
        s_p_e_hide_sub_button_handler,
        start_handler,
        not_imp_handler,
        echo_handler,
        unknown_handler]