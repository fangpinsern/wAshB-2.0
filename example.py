import schedule
import time, datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

led = 26
now = datetime.datetime.now()
nowTime = datetime.datetime.now().time()

actionWord = ""
actionWord2 = ""
useCheckNumber = ""

alreadyOpened = False
lastUpdated = now 

#t1 is the initial time
#t2 is the current time
def diffInTime(t1, t2):
    c = t2 - t1
    timeDiff = divmod(c.days * 86400 + c.seconds, 60)
    return timeDiff

#Sends reminder for the clothing
def sendReminder(mArray):
    print("I am here")
    for i in mArray:
        machineUser = i[0]
        if machineUser != 0 and not i[2]:
            if diffInTime(i[1], datetime.datetime.now())[0] > 120:
                telegram_bot.sendMessage(machineUser, "Your laundry has been in the machine for more than 2hrs! It may have already been completed")
                i[2] = True

#convert String to Boolean
def stringToBool(s):
    if s == "True":
        return True
    else:
        return False

def action(msg):
    global useCheckNumber
    global actionWord2
    global actionWord
    global alreadyOpened
    global lastUpdated

    chat_id = msg['chat']['id']
    command = msg['text']

    # if not alreadyOpened:
    #     f = open("status.txt","r")
    #     if f.mode == 'r':

    if not alreadyOpened:
        rf = open("status.txt", "r")
        if rf.mode == 'r':
            contents =rf.read()
            info = contents.split("|")
            print(info)
            for i in range(0,7):
                du = info[i*3]
                if du == "0":
                    machineStatus[i][0] = 0
                else:
                    machineStatus[i][0] = int(info[i*3])
                dt = info[i*3 + 1]
                if dt != "0":
                    machineStatus[i][1] = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
                machineStatus[i][2] = stringToBool(info[i*3 + 2])
            print(machineStatus)
        alreadyOpened = True

    print ('Recieved: ', command)
    print (nowTime)

    keyboard = ReplyKeyboardMarkup(keyboard=[['/start', '/done'], ['/use', '/status'], ["/notify", "/reset"]])
    numberkeyboard = ReplyKeyboardMarkup(keyboard=[['1', '2', '3'], ['4', '5', '6'], ['7', '/reset']])
    if command != "/reset":
        if actionWord == "" and actionWord2 == "":
            
            if "/start" in command:
                message = "Hi, how may i help you today?\n"
                message = message + "/start - Starts the bot and get help\n"
                message = message + "/done - When you are done using the machine\n"
                message = message + "/use - When you want to use a washing machine\n"
                message = message + "/notify - Notify the person that his/her laundry is ready for collection\n"
                message = message + "/reset - go back to the main page\n"
                message = message + "/status - Check the status of the laundrette\n\n"
                message = message + "Your small gesture would make it more convienient for everyone in the block."
                

            if "/done" in command:
                # found = False
                # machineCounter = 1
                # machineNumber = 0
                # for j in machineStatus:
                #     if(j[0] == chat_id):
                #         found = True
                #         machineNumber = machineCounter
                #     else:
                #         machineCounter = machineCounter + 1
                
                # if found:
                #     message = "Thank you for collecting your clothes! Hope you have a nice day"
                #     machineStatus[machineNumber - 1][0] = 0
                # else:
                #     message = "You are not using any machines at the moment!"
                message = "Which machine is done?"
                keyboard = numberkeyboard
                actionWord = "done"

            if "/use" in command:
                message = "Which machine would you like to use?"
                keyboard = numberkeyboard
                actionWord = "use"

            if "/status" in command:
                message = ""
                for x in range(7):
                    a = str(x + 1)
                    if(machineStatus[x][0] == 0):
                        message = message + a + " is Available\n"
                    else:
                        message = message + a + " is Unavailable (Time used: " + str(diffInTime(machineStatus[x][1], datetime.datetime.now())[0]) + " minutes)\n"
                message = message + "\n"
                for i in range(7):
                    mach = machineStatus[i]
                    if mach[0] == chat_id:
                        message = message + "Currently using: " + str(i+1) + "\n"
                s2 = lastUpdated.strftime("%d/%m/%Y, %H:%M:%S")
                message = message + "\n"
                message = message + "Last Updated: " + s2
            if"/notify" in command:
                message = "Who would you like to notify?"
                keyboard = numberkeyboard
                # keyboard = ReplyKeyboardMarkup(keyboard=[['/surprise'], ['/expected']])
                actionWord = "notify"
            
            # telegram_bot.sendMessage(chat_id, message, reply_markup=keyboard)

        elif actionWord and not actionWord2:
            if actionWord == "done":
                # found = False
                # machineCounter = 1
                # machineNumber = 0
                # for j in machineStatus:
                #     if(j[0] == chat_id):
                #         found = True
                #         machineNumber = machineCounter
                #     else:
                #         machineCounter = machineCounter + 1
                
                # if found:
                #     message = "Thank you for collecting your clothes! Hope you have a nice day"
                #     machineStatus[machineNumber - 1][0] = 0
                # else:
                #     message = "You are not using any machines at the moment!"
                machineNumber = int(command)
                if machineStatus[machineNumber - 1][0] == 0:
                    message = "Machine is currently not in use"
                else:
                    if(machineStatus[machineNumber - 1][0] == chat_id):
                        message = "Thank you for colleting your clothes! Hope you have a great day"
                        machineStatus[machineNumber - 1][0] = 0
                        machineStatus[machineNumber - 1][1] = 0
                        machineStatus[machineNumber - 1][2] = False
                        lastUpdated = datetime.datetime.now()

                    else:
                        message = "These are not your clothes!"

            elif actionWord == "use":
                machineNumber = int(command)
                if machineStatus[machineNumber - 1][0] != 0:
                    message = "Is the machine empty and the person forgot to indicate?"
                    keyboard = ReplyKeyboardMarkup(keyboard=[["yes"], ["no"], ["/reset"]])
                    actionWord2 = "useCheck"
                    useCheckNumber = machineNumber
                else:
                    message =  "Remember to come back when you receive the done message"
                    machineConfig = machineStatus[machineNumber - 1]
                    machineConfig[0] = chat_id
                    machineConfig[1] = datetime.datetime.now()
                    machineConfig[2] = False
                    lastUpdated = datetime.datetime.now()

            elif actionWord == "notify":
                machineNumber = int(command)
                if machineStatus[machineNumber - 1][0] == 0:
                    message = "Machine is currently not in use"
                else:
                    if(machineStatus[machineNumber - 1][0] == chat_id):
                        message = "This is your own clothes"
                    else:
                        telegram_bot.sendMessage(machineStatus[machineNumber - 1][0], "Your clothes are done. Do collect them soon as some one else may need to use it")
                        message =  "We have notified the user, please give the user 5mins to arrive."

                # actionWord2 = command
                
                # if actionWord2 == "/surprise":
                #     message = "Which machine surprised you?"
                #     keyboard = ReplyKeyboardMarkup(keyboard=[['1', '2', '3'], ['4', '5']])
                # elif actionWord2 == "/expected":
                #     message = "Which machine?"
                #     keyboard = ReplyKeyboardMarkup(keyboard=[['1', '2', '3'], ['4', '5']])
            
            actionWord = ""
            # telegram_bot.sendMessage(chat_id, message, reply_markup=keyboard)

        else:
            # userID = 39187936
            # machineNumber = int(command)
            # if actionWord2 == "/surprise":
            #     message = "We have notified the block chat!"
            #     message2 = "Hi, machine " + str(machineNumber) + " is in use but no one informed me!! Kindly let me know who has used it!"
            #     telegram_bot.sendMessage(userID, message2)
            # elif actionWord2 == "/expected":
            #     if machineStatus[machineNumber - 1][0] == 0:
            #         message = "Machine is currently not in use"
            #     else:
            #         if(machineStatus[machineNumber - 1][0] == chat_id):
            #             message = "This is your own clothes"
            #         else:
            #             telegram_bot.sendMessage(machineStatus[machineNumber - 1][0], "Your clothes are done. Do collect them soon as some one else may need to use it")
            #             message =  "We have notified the user, please give the user 5mins to arrive."
            #  else:
            if actionWord2 == "useCheck":
                if command == "yes":
                    machineNumber = useCheckNumber
                    telegram_bot.sendMessage(machineStatus[machineNumber - 1][0], "It seems that you are done with the machine.\n Please remember to let me know next time!", reply_markup=keyboard)
                    machineStatus[machineNumber - 1][0] = chat_id
                    machineStatus[machineNumber - 1][1] = datetime.datetime.now()
                    machineStatus[machineNumber - 1][2] = False
                    lastUpdated = datetime.datetime.now()
                    message = "Okay, we have updated to you being the user of the machine! Remember to collect your clothes! :)"

                if command == "no":
                    message = "These are not your clothes!"

            actionWord = ""
            actionWord2 = ""
            keyboard = ReplyKeyboardMarkup(keyboard=[['/start', '/done'], ['/use', '/status'], ["/notify", "/reset"]])
            actionWord2 = ""
                
        telegram_bot.sendMessage(chat_id, message, reply_markup=keyboard)

    else:
        actionWord = ""
        actionWord2 = ""
        keyboard = ReplyKeyboardMarkup(keyboard=[['/start', '/done'], ['/use', '/status'], ["/notify", "/reset"]])
        message = "Back to homepage!"
        telegram_bot.sendMessage(chat_id, message, reply_markup=keyboard)

    f= open("status.txt","w+")
    for i in range(0,7):
        chat_ID = machineStatus[i][0]
        startTime = machineStatus[i][1]
        hasNotified = machineStatus[i][2]
        help = str(chat_ID) + "|" + str(startTime) + "|" + str(hasNotified) + "|"
        f.write(help)
    f.close()


machineStatus = [[0,0,False],[0,0, False],[0,0, False],[0,0, False],[0,0, False],[0,0,False],[0,0,False]]
    
schedule.every(10).seconds.do(sendReminder, machineStatus)

testBot = telepot.Bot('989321353:AAHpC8w6BAcfj6NM9Nz5hQuQF7KUl_Oj8-0')
mainBot = telepot.Bot('930788863:AAGbxJ4CwV-z8hCjky0lqE13Cgda-3S59qc')
telegram_bot = testBot
print(telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()
print ('Up and Running')

while 1:
    schedule.run_pending()
    time.sleep(10)