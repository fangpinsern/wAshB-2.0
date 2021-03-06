import logging
import os
import random
import sys
import pickle

from session.session import Session
from machineFront.machineFront import MachineFront
from machineManager.machineManager import MachineManager
from admin.adminManager import AdminManager
from botUtils.keyboards import mainMenuKeyboard, startKeyboard, restartKeyboard, machineTypeKeyboard, adminCommandsKeyboard, mainMenuAdminKeyboard
from botUtils.messages import startMessage, useMachineQuestion, machineInUseError, machineDoesNotExistError, invalidSettingError, invalidUserError, invalidMachineError, invalidInputError, userNotUsingMachinesError, doneWithMachineMessage, machineInfoMessage
from datetime import datetime

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Enable logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
firstAdmin = os.getenv("ADMIN")
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
adminManager = AdminManager(firstAdmin)
userSessions = Session("sessionStorage.pickle")

## User command handlers
def start_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if manager.isBannedUser(username):
        stopBannedUsers(update, context)
        return
    logger.info("User {} started bot".format(update.effective_user["id"]))
    menuKeyboard = mainMenuKeyboard
    if adminManager.adminIdExist(username):
        menuKeyboard = mainMenuAdminKeyboard
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=startMessage, reply_markup=menuKeyboard)


def restart_handler(update: Update, context: CallbackContext):
    logger.info("User {} restarted bot".format(update.effective_user["id"]))
    username = update.effective_user["username"]
    if(userSessions.user_exist(username)):
        userSessions.end_session(username)

    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=startMessage, reply_markup=startKeyboard)


def use_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if manager.isBannedUser(username):
        stopBannedUsers(update, context)
        return
    logger.info("User {} is using machine".format(username))
    userSessions.start_session(username, "/use")
    context.bot.sendMessage(
        chat_id=update.effective_user["id"], text=useMachineQuestion, reply_markup=manager.getKeyboard())


# chosenMachineNum = 0

#handles all general queries that are not commands
def choose_machine_handler(update: Update, context: CallbackContext):
    # global chosenMachineNum
    userInput = update.message.text
    username = update.effective_user["username"]
    chatId = update.effective_user["id"]
    isAdmin = adminManager.adminIdExist(username)
    lastCommand = userSessions.get_last_command(username)

    if manager.isBannedUser(username):
        stopBannedUsers(update, context)
        return
    if (lastCommand == "/use"):
        if(manager.nameExist(userInput)):
            chosenMachine = manager.getMachineByName(userInput)
            if (chosenMachine.isInUse()):
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text=machineInUseError, reply_markup=manager.getKeyboard())
            else:
                chosenMachineName = userInput
                custom_keyboard = chosenMachine.settingsKeyboard
                settingKeyboard = ReplyKeyboardMarkup(custom_keyboard)
                userSessions.update_session(username, "machineNumber")
                userSessions.add_passing_arguments(username, [userInput])
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Please choose your setting so I can notify you when it is done!", reply_markup=settingKeyboard)

        else:
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text=machineDoesNotExistError, reply_markup=manager.getKeyboard())

    elif (lastCommand == "machineNumber"):
        chosenMachineNum = userSessions.get_passing_arguments(username)[0]
        if(manager.useMachine(chosenMachineNum, username, chatId, userInput)):
            logger.info("Machine start time is {} and end time is {}".format(
                manager.getMachineByName(chosenMachineNum).getStartTime(), manager.getMachineByName(chosenMachineNum).getEndTime()))
            userSessions.end_session(username)
            logger.info("User {} is using {}".format(username, chosenMachineNum))
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="Noted!", reply_markup=restartKeyboard)
        else:
            logger.info("Setting chosen is invalid")
            custom_keyboard=manager.getMachineByName(chosenMachineNum).settingsKeyboard
            settingKeyboard = ReplyKeyboardMarkup(custom_keyboard)
            context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text=invalidSettingError, reply_markup=settingKeyboard)


    elif (lastCommand == "/done"):
        if(manager.nameExist(userInput)):
            validDoneUse = manager.doneUse(userInput, chatId)
            if validDoneUse:
                logger.info("User {} is done with machine {}".format(
                    username, userInput))
                userSessions.end_session(username)
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Thank you! Hope to see you again soon", reply_markup=restartKeyboard)
            else:
                context.bot.sendMessage(chat_id=update.effective_user["id"], text=invalidUserError, reply_markup=restartKeyboard)
        else:
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text=invalidMachineError, reply_markup=manager.getMachineUsedByUserKeyboard(chatId))

    elif (lastCommand == "/info"):
        if(manager.nameExist(userInput)):
            chosenMachine = manager.getMachineByName(userInput)
            userSessions.end_session(username)
            context.bot.sendMessage(chat_id=update.effective_user["id"], text=chosenMachine.getInfoMessage(), reply_markup=restartKeyboard)
            
    elif (lastCommand == "/addAdmin"):
        validAddAdmin = adminManager.addAdmin(userInput)
        if validAddAdmin:
            logger.info("User {} has been added as admin".format(userInput))
            userSessions.end_session(username)
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="Admin {} has been added".format(userInput), reply_markup=restartKeyboard)
        else:
            logger.info("The admin user may already exist. Or there is an error in adding")
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="User may already be an admin. use /show to see your your admins!", reply_markup=restartKeyboard)

    elif (lastCommand == "/removeAdmin"):
        if adminManager.isMaster(userInput):
            logger.info("Master tried to remove himself")
            context.bot.sendMessage(
                chat_id=update.effective_user["id"], text="You cant remove master from admin...", reply_markup=restartKeyboard)
        
        else: 
            validRemoveAdmin = adminManager.removeAdmin(userInput)
            if validRemoveAdmin:
                logger.info("User {} has been removed as admin".format(userInput))
                userSessions.end_session(username)
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="Admin {} has been removed".format(userInput), reply_markup=restartKeyboard)
            else:
                logger.info("The admin user does not exist. Or there is an error in removing")
                context.bot.sendMessage(
                    chat_id=update.effective_user["id"], text="User is not an admin. Use /show to see your your admins!", reply_markup=restartKeyboard)

    elif (lastCommand == "/addMachineType"):
        if isAdmin:
            if(userInput != "front" and userInput != "top"):
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="Machine Type invalid. Please use the options given", reply_markup=machineTypeKeyboard)
            else:
                userSessions.update_session(username, "/addMachineName")
                userSessions.add_passing_arguments(username, [userInput])
                logger.info("User {} has named the machine {}".format(username, userInput))
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="What would you name the machine?", reply_markup=restartKeyboard)

    elif (lastCommand == "/addMachineName"):
        if isAdmin:
            machineType = userSessions.get_passing_arguments(username)[0]
            if manager.nameExist(userInput):
                logger.info("Machine name exist")
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="This name already exist. Please try again", reply_markup=restartKeyboard)
            else:
                newMachine = MachineFront(machineType, userInput)
                manager.addMachine(newMachine)
                logger.info("Machine has been added")
                userSessions.end_session(username)
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="Machine has been added! You can see it using the /status command", reply_markup=restartKeyboard)

    elif (lastCommand == "/removeMachine"):
        if isAdmin:
            validRemoveMachine = manager.removeMachineByName(userInput)
            if validRemoveMachine:
                logger.info("User {} would like to remove machine {}".format(username, userInput))
                userSessions.end_session(username)
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="Machine has been removed! You can check by using the /status command", reply_markup=restartKeyboard)
            else:
                logger.info("User {} would like to remove machine {}".format(username, userInput))
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="Machines does not exist. Please try again! The machine names should be provided at the keyboard. If not, you may want to restart the process", reply_markup=restartKeyboard)

    elif (lastCommand == "/banUser"):
        if isAdmin:
            if userInput == username:
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="You cannot ban yourself")
                return
            elif adminManager.adminIdExist(userInput):
                context.bot.sendMessage(chat_id=update.effective_user["id"], text="You cannot ban an admin. Please remove this admin before banning")
                return
            manager.banUser(userInput)
            logger.info("User {} has banned {}".format(username, userInput))
            userSessions.end_session(username)
            context.bot.sendMessage(chat_id=update.effective_user["id"], text="User {} has been banned!".format(userInput))

    else:
        update.message.reply_text(invalidInputError)


def status_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    logger.info("User {} asked for status".format(username))
    status = manager.printStatus()
    update.message.reply_text(status)


def done_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if manager.isBannedUser(username):
        stopBannedUsers(update, context)
        return

    chatId = update.effective_user["id"]
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



## Scheduling reminders
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

## masterHandlers
def add_admin_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if (adminManager.isMaster(username)):
        userSessions.start_session(username, "/addAdmin")
        logger.info("User {} would like to add admin users".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Please enter the username of the new admin", reply_markup=ReplyKeyboardRemove())       
    else: 
        logger.info("User {} tried to access root/admin priviledges".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have root/admin privileges", reply_markup=restartKeyboard)

def remove_admin_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.isMaster(username):
        userSessions.start_session(username, "/removeAdmin")
        logger.info("User {} would like to remove admin users".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Please enter the username you would like to remove", reply_markup=adminManager.getAdminKeyboard())
    else:
        logger.info("User {} tried to access root/admin priviledges".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have root/admin privileges", reply_markup=restartKeyboard)  

def show_admin_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.isMaster(username):
        logger.info("User {} would like to see the list of admins".format(username))
        listOfAdmins = adminManager.getListOfAdmins()
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text=listOfAdmins, reply_markup=restartKeyboard)


# AdminHandlers
def accessAdminCommands(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.adminIdExist(username):
        context.bot.sendMessage(chat_id=update.effective_user["id"], text="You are in the admin controls", reply_markup=adminCommandsKeyboard)

def add_machine_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.adminIdExist(username):
        logger.info("User {} would like to add machines".format(username))
        userSessions.start_session(username, "/addMachineType")
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="What is the type of the machine?", reply_markup=machineTypeKeyboard)  
    else:
        logger.info("User {} does not have the rights to add machines".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have the rights to this command", reply_markup=restartKeyboard)

def remove_machine_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.adminIdExist(username):
        logger.info("User {} would like to remove machines".format(username))
        userSessions.start_session(username, "/removeMachine")
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Which machine would you like to remove?", reply_markup=manager.getKeyboard())
    else:
        logger.info("User {} does not have rights to remove machines".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have the rights to this command", reply_markup=restartKeyboard)

def banUser_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.adminIdExist(username):
        logger.info("User {} would like to ban a user".format(username))
        userSessions.start_session(username, "/banUser")
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Please let me know the username of the person you would like to ban")
    else:
        logger.info("User {} does not have rights to remove ban users".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have the rights to this command", reply_markup=restartKeyboard)

def viewBannedUsers_handler(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    if adminManager.adminIdExist(username):
        logger.info("User {} would like to check banned users".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="Banned Users:\n" + manager.getBannedUserString())
    else:
        logger.info("User {} does not have rights to view this".format(username))
        context.bot.sendMessage(
            chat_id=update.effective_user["id"], text="You do not have the rights to this command", reply_markup=restartKeyboard)

# util Functions
def stopBannedUsers(update: Update, context: CallbackContext):
    username = update.effective_user["username"]
    context.bot.sendMessage(chat_id=update.effective_user["id"], text="You have been banned!", reply_markup=ReplyKeyboardRemove())
    logger.info("Banned user {} is trying to use the bot".format(username))
    return


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)
    j = updater.job_queue
    
    # User commands
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("use", use_handler))
    updater.dispatcher.add_handler(CommandHandler("status", status_handler))
    updater.dispatcher.add_handler(CommandHandler("print", print_sessions))
    updater.dispatcher.add_handler(CommandHandler("restart", restart_handler))
    updater.dispatcher.add_handler(CommandHandler("done", done_handler))
    updater.dispatcher.add_handler(CommandHandler("info", info_handler))

    # master commands
    updater.dispatcher.add_handler(CommandHandler("addAdmin", add_admin_handler))
    updater.dispatcher.add_handler(CommandHandler("removeAdmin", remove_admin_handler))
    updater.dispatcher.add_handler(CommandHandler("show", show_admin_handler))

    # admin commands
    updater.dispatcher.add_handler(CommandHandler("addMachine", add_machine_handler))
    updater.dispatcher.add_handler(CommandHandler("removeMachine", remove_machine_handler))
    updater.dispatcher.add_handler(CommandHandler("config", accessAdminCommands))
    updater.dispatcher.add_handler(CommandHandler("ban", banUser_handler))
    updater.dispatcher.add_handler(CommandHandler("viewBan", viewBannedUsers_handler))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text, choose_machine_handler))

    job_minute = j.run_repeating(callback_minute, interval=10, first=0)
    run(updater)
    