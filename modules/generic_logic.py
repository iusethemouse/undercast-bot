"""
generic_logic.py

Trivial bot routines to handle supplementary commands and tasks.
"""

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    """
    Invoked by either starting a first-time conversation with the bot, or by sending it
    a /start command any time after that.
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
This is <b>Undercast</b>.

- Search for podcasts
- Download and share episodes
- Get notified of new releases

To get started, just send me a message with a search term.
""", parse_mode='html')
    

def not_imp_button(update, context):
    """
    A callback to catch any features not yet implemented (i.e. subscriptions).
    """
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.send_message(chat_id=update.effective_chat.id,
                     text='Feature is not yet implemented.')
    
    
def unknown(update, context):
    """
    Catches unknown commands.
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Unknown command.")
    
    
def error(update, context):
    """
    Prints out errors to console.
    """
    logger.warning('Update caused error "%s"', context.error)
