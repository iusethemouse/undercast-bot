"""
handlers.py

This contains one dict with declarations of all handlers.
"""

from telegram.ext import (CommandHandler, 
                          MessageHandler, 
                          CallbackQueryHandler,
                          Filters)

# Local imports
from . import search_logic
from . import generic_logic

handlers = {
        # Command handlers
        "start_handler": CommandHandler('start', generic_logic.start),

        # Search handler. All plaintext messages are processed as search queries
        "search_handler": MessageHandler(Filters.text, search_logic.search),

        # Displays selected podcast
        "podcast_selection_callback_handler": CallbackQueryHandler(search_logic.podcast_selection_callback, pattern='^[0-9]+$'),

        # Episode list navigation
        "view_episodes_callback_handler": CallbackQueryHandler(search_logic.view_episodes_callback, pattern='^episodes[0-9]+$'),
        "back_to_podcast_callback_handler": CallbackQueryHandler(search_logic.back_to_podcast_callback, pattern='^return[0-9]+$'),
        "next_page_of_episodes_callback_handler": CallbackQueryHandler(search_logic.next_page_of_episodes_callback, pattern='^episodes_next_page$'),
        "prev_page_of_episodes_callback_handler": CallbackQueryHandler(search_logic.prev_page_of_episodes_callback, pattern='^episodes_prev_page$'),
        "last_page_of_episodes_callback_handler": CallbackQueryHandler(search_logic.last_page_of_episodes_callback, pattern='^episodes_last_page$'),
        "first_page_of_episodes_callback_handler": CallbackQueryHandler(search_logic.first_page_of_episodes_callback, pattern='^episodes_first_page$'),

        # Display selected episode
        "episode_selection_callback_handler": CallbackQueryHandler(search_logic.episode_selection_callback, pattern='^[0-9]+_[0-9]+$'),
        "return_to_episode_list_callback_handler": CallbackQueryHandler(search_logic.return_to_episode_list_callback, pattern='^[0-9]+return_to_episode_list[0-9]+$'),
        "download_episode_callback_handler": CallbackQueryHandler(search_logic.download_episode_callback, pattern='^[0-9]+download[0-9]+$'),
        "view_shownotes_callback_handler": CallbackQueryHandler(search_logic.view_shownotes_callback, pattern='^[0-9]+shownotes[0-9]+$'),
        "hide_shownotes_callback_handler": CallbackQueryHandler(search_logic.hide_shownotes_callback, pattern='^hide_shownotes$'),

        # Generic handlers
        "not_imp_handler": CallbackQueryHandler(generic_logic.not_imp_button, pattern='^n_i$'),
        "unknown_handler": MessageHandler(Filters.command, generic_logic.unknown)
}