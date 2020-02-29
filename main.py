import logging
import os
import random
import sys

from session import Session
from machineFront import MachineFront

from datetime import datetime

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import Update, ReplyKeyboardMarkup

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

# format: [inUse: boolean, user: String]
# machineUsage = [[False, ""], [False, ""], [False, ""], [
#     False, ""], [False, ""], [False, ""], [False, ""], [False, ""]]

machine1 = MachineFront("front")
machine2 = MachineFront("front")
machine3 = MachineFront("top")
machine4 = MachineFront("front")
machine5 = MachineFront("top")
machine6 = MachineFront("front")
machine7 = MachineFront("front")
machine8 = MachineFront("front")

machineStorage = [machine1, machine2, machine3,
                  machine4, machine5, machine6, machine7, machine8]

userSessions = Session()


def start_handler(update: Update, context: CallbackContext):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    custom_keyboard = [['/use', '/status'],
                       ['/print', "/restart"],["/done"]]
    startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text="Hello from Python!\nPress /random to get random number", reply_markup=startKeyboard)
    # update.message.reply_text(
    #     "Hello from Python!\nPress /random to get random number", startKeyboard)


def restart_handler(update: Update, context: CallbackContext):
    logger.info("User {} restarted bot".format(update.effective_user["id"]))

    username = update.effective_user["username"]
    if(userSessions.user_exist(username)):
        userSessions.end_session(username)

    custom_keyboard = [['/start']]
    startKeyboard = ReplyKeyboardMarkup(custom_keyboard)

    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text="Hello from Python!\nPress /random to get random number", reply_markup=startKeyboard)


def use_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    #     logger.info("User {} entered an invalid machine number of {}".format(
    #         username, machine_number))
    logger.info("User {} is using machine".format(username))
    userSessions.start_session(username, "/use")
    custom_keyboard = [['1', '2', '3', '4'],
                       ['5', '6', '7', '8'], ['/restart']]
    startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text="Which machine would you like to use?", reply_markup=startKeyboard)


chosenMachineNum = 0


def choose_machine_handler(update: Update, context: CallbackContext):
    global chosenMachineNum
    userInput = update.message.text
    username = update.effective_user["username"]
    chatId = update.effective_user["id"]

    if (userInput.isdigit() and userSessions.get_last_command(username) == "/use"):
        if(int(userInput) < 9 and int(userInput) > 0):
            chosenMachine = machineStorage[int(userInput) - 1]
            if (chosenMachine.isInUse()):
                custom_keyboard = [['1', '2', '3', '4'],
                                   ['5', '6', '7', '8'], ['/restart']]
                startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="That machine is in use! please choose another one", reply_markup=startKeyboard)
            else:
                chosenMachineNum = int(userInput)
                custom_keyboard = chosenMachine.settingsKeyboard
                startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
                userSessions.update_session(username, "machineNumber")
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Please choose your setting so I can notify you when it is done!", reply_markup=startKeyboard)

        else:
            custom_keyboard = [['1', '2', '3', '4'],
                               ['5', '6', '7', '8'], ['/restart']]
            startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="Machine does not exist. Please try again", reply_markup=startKeyboard)

    elif (userSessions.get_last_command(username) == "machineNumber"):
        chosenMach = machineStorage[chosenMachineNum - 1]
        machineStorage[chosenMachineNum -
                       1].useMachine(username, chatId, userInput)
        logger.info("Machine start time is {} and end time is {}".format(
            chosenMach.getStartTime(), chosenMach.getEndTime()))
        custom_keyboard = [['/restart']]
        startKeyboard1 = ReplyKeyboardMarkup(custom_keyboard)
        userSessions.end_session(username)
        logger.info("User {} is using {}".format(username, chosenMachineNum))
        chosenMachineNum = 0
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Noted!", reply_markup=startKeyboard1)

    elif (userInput.isdigit() and userSessions.get_last_command(username) == "/done"):
        if(int(userInput) < 9 and int(userInput) > 0):
            chosenMachine = machineStorage[int(userInput) - 1]
            if chosenMachine.chatId == chatId:
                chosenMachine.doneUse()
                logger.info("User {} is done with machine {}".format(
                    username, userInput))
                custom_keyboard = [['/restart']]
                startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
                userSessions.end_session(username)
                chosenMachineNum = 0
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Thank you! Hope to see you again soon", reply_markup=startKeyboard)
            else:
                update.message.reply_text("You are not using this machine")
        else:
            custom_keyboard = [['1', '2', '3', '4'],
                               ['5', '6', '7', '8'], ['/restart']]
            startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="Machine does not exist. Please try again", reply_markup=startKeyboard)

    else:
        update.message.reply_text("Invalid input. You may want to restart with /restart command.")


def status_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    logger.info("User {} asked for status".format(username))
    status = ""
    machineNum = 1
    for machine in machineStorage:
        status = status + machine.printStatus(machineNum)
        machineNum = machineNum + 1
    update.message.reply_text(status)


def done_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    chatId = update.effective_user["id"]
    userExist = False
    machinesInUse = []

    counter = 1
    for machine in machineStorage:
        if machine.chatId == chatId:
            userExist = True
            machinesInUse.append([str(counter)])
        counter = counter + 1

    if not userExist:
        logger.info("User {} made an invalid action".format(chatId))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You are not using any machines right now", reply_markup=ReplyKeyboardMarkup([["/restart"]]))

    else:
        userSessions.start_session(username, "/done")
        custom_keyboard = machinesInUse
        startKeyboard = ReplyKeyboardMarkup(custom_keyboard)
        logger.info("User {} is trying to done some machines".format(chatId))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Which machine how you completed using?", reply_markup=startKeyboard)


# def info_handler(update: Update, context: CallbackContext):
#     userSessions.start_session(username, "/info")
#     custom_keyboa

def print_sessions(update: Update, context: CallbackContext):
    replyMessage = userSessions.to_string()
    if not replyMessage:
        update.message.reply_text("No sessions in progress")
    else:
        update.message.reply_text(replyMessage)


def callback_minute(context: CallbackContext):
    now = datetime.now()
    for machine in machineStorage:
        if(machine.chatId != 0 and not machine.hasReminded):
            if machine.getEndTime() < now:
                chat_id = machine.chatId
                context.bot.sendMessage(
                    chat_id=chat_id, text='Your Laundry is done')
                logger.info("User {} end time is {} and now is {}".format(
                    chat_id, machine.getEndTime(), now))
                machine.doneUse()
    logger.info("Scheduler have ran {}".format(now))


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)
    j = updater.job_queue
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("use", use_handler))
    updater.dispatcher.add_handler(CommandHandler("status", status_handler))
    updater.dispatcher.add_handler(CommandHandler("print", print_sessions))
    updater.dispatcher.add_handler(CommandHandler("restart", restart_handler))
    updater.dispatcher.add_handler(CommandHandler("done", done_handler))
    # updater.dispatcher.add_handler(CommandHandler("info", info_handler))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text, choose_machine_handler))

    job_minute = j.run_repeating(callback_minute, interval=10, first=0)
    run(updater)
