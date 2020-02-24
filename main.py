import logging
import os
import random
import sys

from session import Session

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram import Update

# Enable logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("no MODE specified")
    sys.exit(1)


machineUsage = [[False, ""], [False, ""], [False, ""], [
    False, ""], [False, ""], [False, ""], [False, ""], [False, ""]]

userSessions = Session()

def start_handler(update: Update, context: CallbackContext):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text(
        "Hello from Python!\nPress /random to get random number")


def random_handler(update: Update, context: CallbackContext):
    number = random.randint(0, 10)
    logger.info("User {} randomed number {}".format(
        update.effective_user["id"], number))
    update.message.reply_text("Random number: {}".format(number))


def use_handler(update: Update, context: CallbackContext):
    if (not context.args):
        update.message.reply_text(
            "Input machine number after the command. \nFor example, '/use 1' to use machine 1")
        return

    machine_number = int(context.args[0])
    username = update.effective_user["username"]

    if (machine_number > 8 or machine_number < 1):
        logger.info("User {} entered an invalid machine number of {}".format(
            username, machine_number))
        update.message.reply_text("Machine number does not exist")

    else:
        logger.info("User {} is using machine {}".format(
            username, machine_number))
        userSessions.start_session(username, "/use")

        machine_in_use(machine_number, username)
        update.message.reply_text("What help do you need?" + context.args[0])


def status_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    logger.info("User {} asked for status".format(username))
    status = ""
    for machine in machineUsage:
        if machine[0]:
            status = status + "1"
        else:
            status = status + "0"
    update.message.reply_text(status)

def print_sessions(update: Update, context: CallbackContext):
    update.message.reply_text(userSessions.to_string())


def machine_in_use(machine_number, username):
    machineUsage[machine_number - 1] = [True, username]


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("random", random_handler))
    updater.dispatcher.add_handler(CommandHandler("use", use_handler))
    updater.dispatcher.add_handler(CommandHandler("status", status_handler))
    updater.dispatcher.add_handler(CommandHandler("print", print_sessions))

    run(updater)
