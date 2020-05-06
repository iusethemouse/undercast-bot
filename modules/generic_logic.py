"""General bot logic not assigned to any particular routine.

Error handling, unknown command handling, feature not implemented handling,
and others.

"""

# Global imports
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    """
    Called when user initialises a first-time conversation with the bot.
    Also called when user erases chat history and reinitialises conversation.
    Can be called manually with /start.

    Besides the welcome message, also checks if the persistance pickle is correctly
    set up for storing podcasts and episodes.
    TODO: reconfigure the pickle to only store file IDs for podcast artwork and episodes
    to minimise pickle size. Might have to store entire podcast objects for subscriptions though.
    """

    for k in ['podcasts', 'episodes']:
        if k not in context.bot_data:
            context.bot_data[k] = dict()
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
This is <b>Undercast</b>.

- Search for podcasts using any related term: podcast name, artist, topic, genre.
- Download and listen to episodes.
- Share favourite podcasts and episodes with anyone.

To get started, type a search term after the /search command.
""", parse_mode='html')


def echo(update, context):
    """
    A simple message handler that repeats messages sent by the user.
    Used to check if the bot is online.
    """

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)
    

def not_imp_button(update, context):
    """
    Catches a "n_i" query sent by a button for a non-implemented feature,
    sends user a message saying so.
    """

    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.send_message(chat_id=update.effective_chat.id,
                     text='Feature is not yet implemented.')
    
    
def unknown(update, context):
    """
    Used to indicate unrecognised commands.
    """

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Unknown command.")
    
    
def error(update, context):
    """
    When encountering any errors caused when processing an update,
    prints out the relevant information to console.
    """

    logger.warning('Update caused error "%s"', context.error)
