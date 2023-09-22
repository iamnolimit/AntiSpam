import logging
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from collections import defaultdict

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create a dictionary to store message counts for each user
user_message_counts = defaultdict(int)

# Create a dictionary to store chat IDs and spam detection counts
chat_spam_counts = defaultdict(lambda: defaultdict(int))

# Define a function to handle incoming messages


def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    text = update.message.text

    # Check if the user has sent this exact same message before in this chat
    if text not in chat_spam_counts[chat_id]:
        chat_spam_counts[chat_id][text] = 0

    # Increment the message count for this user and chat
    user_message_counts[user_id] += 1
    chat_spam_counts[chat_id][text] += 1

    # Check if the user has sent the same message more than 3 times in this chat
    if user_message_counts[user_id] > 3:
        # Delete the repeated message
        try:
            update.message.delete()
        except Exception as e:
            # Handle the exception (e.g., message already deleted)
            pass
        # Reset the user's message count to prevent further deletion
        user_message_counts[user_id] = 0

    # Check if the chat has received more than 5 messages with the same text within a minute
    if chat_spam_counts[chat_id][text] > 2:
        # Delete the message if it's part of the chat's spam
        try:
            update.message.delete()
        except Exception as e:
            # Handle the exception (e.g., message already deleted)
            pass
    else:
        # Reset the chat's spam detection count for this text after 1 minute
        context.job_queue.run_once(
            reset_chat_spam_count, 60, context=(chat_id, text))

# Define a function to reset the chat's spam detection count for a specific text


def reset_chat_spam_count(context: CallbackContext):
    chat_id, text = context.job.context
    chat_spam_counts[chat_id][text] = 0


def main() -> None:
    # Initialize the Telegram Bot with your API token
    updater = Updater("6657595722:AAHyaamER0uFriiUdmg-RBuSF_XIQ0d6A5g")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register a message handler to handle all messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    # Start the Bot
    updater.start_polling()

    # Run the Bot until you send a signal to stop (e.g., Ctrl+C)
    updater.idle()


if __name__ == '__main__':
    main()
