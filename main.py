import logging
import os
import random
import sys
import pickle

from session.session import Session
from machineFront.machineFront import MachineFront
from machineManager.machineManager import MachineManager
from botUtils.keyboards import mainMenuKeyboard, startKeyboard, restartKeyboard
from botUtils.messages import startMessage, useMachineQuestion, machineInUseError, machineDoesNotExistError, invalidSettingError, invalidUserError, invalidMachineError, invalidInputError, userNotUsingMachinesError, doneWithMachineMessage, machineInfoMessage
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

machine1 = MachineFront("front", "1")
machine2 = MachineFront("front", "2")
machine3 = MachineFront("top", "3")
machine4 = MachineFront("front", "4")
machine5 = MachineFront("top", "5")
machine6 = MachineFront("front", "6")
machine7 = MachineFront("front", "7")
machine8 = MachineFront("front", "8")

machineStorage = [machine1, machine2, machine3,
                  machine4, machine5, machine6, machine7, machine8]
manager = MachineManager(machineStorage, "machineManager.pickle")

userSessions = Session("sessionStorage.pickle")

## User command handlers
def start_handler(update: Update, context: CallbackContext):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=startMessage, reply_markup=mainMenuKeyboard)


def restart_handler(update: Update, context: CallbackContext):
    logger.info("User {} restarted bot".format(update.effective_user["id"]))

    username = update.effective_user["username"]
    if(userSessions.user_exist(username)):
        userSessions.end_session(username)

    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=startMessage, reply_markup=startKeyboard)


def use_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    logger.info("User {} is using machine".format(username))
    userSessions.start_session(username, "/use")
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=useMachineQuestion, reply_markup=manager.getKeyboard())


chosenMachineNum = 0

#handles all general queries that are not commands
def choose_machine_handler(update: Update, context: CallbackContext):
    global chosenMachineNum
    userInput = update.message.text
    username = update.effective_user["username"]
    chatId = update.effective_user["id"]

    if (userInput.isdigit() and userSessions.get_last_command(username) == "/use"):
        if(int(userInput) < 9 and int(userInput) > 0):
            chosenMachine = manager.getMachine(int(userInput))
            if (chosenMachine.isInUse()):
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text=machineInUseError, reply_markup=manager.getKeyboard())
            else:
                chosenMachineNum = int(userInput)
                custom_keyboard = chosenMachine.settingsKeyboard
                settingKeyboard = ReplyKeyboardMarkup(custom_keyboard)
                userSessions.update_session(username, "machineNumber")
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Please choose your setting so I can notify you when it is done!", reply_markup=settingKeyboard)

        else:
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text=machineDoesNotExistError, reply_markup=manager.getKeyboard())

    elif (userSessions.get_last_command(username) == "machineNumber"):
        if(manager.useMachine(chosenMachineNum, username, chatId, userInput)):
            logger.info("Machine start time is {} and end time is {}".format(
                manager.getMachine(chosenMachineNum).getStartTime(), manager.getMachine(chosenMachineNum).getEndTime()))
            userSessions.end_session(username)
            logger.info("User {} is using {}".format(username, chosenMachineNum))
            chosenMachineNum = 0
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="Noted!", reply_markup=restartKeyboard)
        else:
            logger.info("Setting chosen is invalid")
            custom_keyboard=manager.getMachine(chosenMachineNum).settingsKeyboard
            settingKeyboard = ReplyKeyboardMarkup(custom_keyboard)
            context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text=invalidSettingError, reply_markup=settingKeyboard)


    elif (userSessions.get_last_command(username) == "/done"):
        if(manager.nameExist(userInput)):
            validDoneUse = manager.doneUse(userInput, chatId)
            if validDoneUse:
                logger.info("User {} is done with machine {}".format(
                    username, userInput))
                userSessions.end_session(username)
                chosenMachineNum = 0
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Thank you! Hope to see you again soon", reply_markup=restartKeyboard)
            else:
                context.bot.sendMessage(chat_id=update.effective_user["id"], text=invalidUserError, reply_markup=restartKeyboard)
        else:
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text=invalidMachineError, reply_markup=manager.getMachineUsedByUserKeyboard(chatId))

    elif (userInput.isdigit() and userSessions.get_last_command(username) == "/info"):
        if(int(userInput) < 9 and int(userInput) > 0):
            chosenMachine = manager.getMachine(int(userInput))
            context.bot.sendMessage(chat_id=update.effective_user["id"], text=chosenMachine.getInfoMessage(), reply_markup=restartKeyboard)
            
    else:
        update.message.reply_text(invalidInputError)


def status_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    logger.info("User {} asked for status".format(username))
    status = manager.printStatus()
    update.message.reply_text(status)


def done_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    chatId = update.effective_user["id"]
    userExist = False
    machinesInUse = manager.getMachineUsedByUser(chatId)

    if len(machinesInUse) == 0:
        logger.info("User {} made an invalid action".format(chatId))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text=userNotUsingMachinesError, reply_markup=restartKeyboard)

    else:
        userSessions.start_session(username, "/done")
        logger.info("User {} is trying to done some machines".format(chatId))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text=doneWithMachineMessage, reply_markup=manager.getMachineUsedByUserKeyboard(chatId))

def info_handler(update: Update, context: CallbackContext):
    username = update.effective_user['username']
    userSessions.start_session(username, "/info")
    logger.info("User {} wants to retrieve information about machines".format(username))
    context.bot.sendMessage(chat_id=update.effective_user["id"], text=machineInfoMessage, reply_markup=manager.getKeyboard())
## End user command handlers

## Debugging handlers
def print_sessions(update: Update, context: CallbackContext):
    replyMessage = userSessions.to_string()
    if not replyMessage:
        update.message.reply_text("No sessions in progress")
    else:
        update.message.reply_text(replyMessage)




def callback_minute(context: CallbackContext):
    now = datetime.now()
    machinesInUse = manager.getMachinesInUse()
    for machine in machinesInUse:
        if(machine.chatId != 0 and not machine.hasReminded):
            if machine.getEndTime() < now:
                chat_id = machine.chatId
                context.bot.sendMessage(
                    chat_id=chat_id, text='Your Laundry in {} is done'.format(machine.getName()))
                logger.info("User {} end time is {} and now is {}".format(
                    chat_id, machine.getEndTime(), now))
                machine.doneUse(chat_id)
                manager.onChange()
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
    updater.dispatcher.add_handler(CommandHandler("info", info_handler))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text, choose_machine_handler))

    job_minute = j.run_repeating(callback_minute, interval=10, first=0)
    run(updater)
    