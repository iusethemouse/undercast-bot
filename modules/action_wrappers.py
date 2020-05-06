# Global imports
import telegram
from functools import wraps


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, 
                                     action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def send_upload_audio_action(func):
    """Sends audio file action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, 
                                     action=telegram.ChatAction.UPLOAD_DOCUMENT)
        return func(update, context,  *args, **kwargs)

    return command_func