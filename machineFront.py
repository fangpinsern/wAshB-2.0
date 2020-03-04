from datetime import datetime, timedelta


class MachineFront:

    frontSettings = [["Cotton 60 with Prewash", 121], ["Cottons 90", 133], ["Cottons 40", 80], ["Cottons Cold", 80], ["Cottons Eco 60", 132], ["Cottons Eco 40", 120], [
        "Synthetics 60", 113], ["Synthetics 40", 105], ["Synthetics Cold", 66], ["Delicates 30", 65], ["Woolen 40", 54], ["Hand Wash 20", 41], ["Mini 30", 29]]

    frontSettingsKeyboard = [["Cotton 60 with Prewash"], ["Cottons 90"], ["Cottons 40"], ["Cottons Cold"], [
        "Cottons Eco 60"], ["Cottons Eco 40"], ["Synthetics 60"], ["Synthetics 40"], ["Synthetics Cold"], ["Delicates 30"], ["Woolen 40"], ["Hand Wash 20"], ["Mini 30"], ["/restart"]]

    frontInfoMessage = "This machine loads from the front!\n Here is a step by step guide on how to use the machine.\n" +\
        "Firstly, put your clothes into the washing machine through the front and close the door.\n\n" + \
        "Next, open the compartment at the top right of the washing machine. Pour your detergent into the most right container.\n\n" + \
        "If you have fabric softener, pour it into the middle compartment. If you are going for 2 cycles, pour more detergent into the right container.\n\n" + \
        "Afterwards, close the container and set the settings dial to the setting you would want to use. Below is a break down of the timings for each setting.\n\n" + \
        "Cotton 60 with prewash: 121 Minutes\n" +\
        "Cottons 90: 133 Minutes\n" + \
        "Cottons 40: 80 Minutes\n" + \
        "Cottons Cold: 80 Minutes\n" + \
        "Cottons Eco 60: 132 Minutes\n" + \
        "Cottons Eco 40: 120 Minutes\n" + \
        "Synthetics 60 : 133 Minutes\n" + \
        "Synthetics 40: 105 Minutes\n" + \
        "Synthetics Cold: 66 Minutes\n" + \
        "Delicates 30: 65 Minutes\n" + \
        "Woolen 40: 54 Minutes\n" + \
        "Hand Wash 20: 41 Minutes\n" + \
        "Mini 30: 29 Minutes"

    topSettings = [["30 Minutes", 30], ["1 Hour", 60],
                   ["1.5 Hours", 90], ["2 Hours", 120]]

    topSettingsKeyboard = [["30 Minutes"], ["1 Hour"],
                           ["1.5 Hours"], ["2 Hours"], ["/restart"]]

    inUse = False
    startTime = 0
    endTime = 0
    username = ""
    chatId = 0
    hasReminded = False
    typeOfMachine = ""
    settings = [["Something is wrong", 0]]
    settingsKeyboard = [["You are not suppose to see this"]]
    infoMessage = "The info message has not been configured yet."

    def __init__(self, typeOfMachine):
        self.typeOfMachine = typeOfMachine
        if typeOfMachine == "front":
            self.settings = self.frontSettings
            self.settingsKeyboard = self.frontSettingsKeyboard
            self.infoMessage = self.frontInfoMessage
        elif typeOfMachine == "top":
            self.settings = self.topSettings
            self.settingsKeyboard = self.topSettingsKeyboard

    def isInUse(self):
        return self.inUse

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime

    def getInfoMessage(self):
        return self.infoMessage

    def getChatId(self):
        return self.chatId

    def useMachine(self, username, chatId, setting):
        validUse = False
        duration = self.getTiming(setting)
        if (duration != -1):
            self.username = username
            self.chatId = chatId
            self.startTime = datetime.now()
            self.endTime = self.startTime + timedelta(minutes=duration)
            self.inUse = True
            validUse = True
        return validUse

    def doneUse(self, chatId):
        validDoneUse = chatId == self.chatId
        if(validDoneUse):
            self.username = ""
            self.startTime = 0
            self.endTime = 0
            self.chatId = 0
            self.inUse = False
        return validDoneUse

    def getTiming(self, setting):
        time = -1
        for setting1 in self.settings:
            if setting1[0] == setting:
                time = setting1[1]

        return time

    def printStatus(self, id):
        if (self.inUse):
            return "Machine {} is in use. Available after {}\n".format(id, self.endTime.strftime("%H:%M:%S"))
        else:
            return "Machine {} is available.\n".format(id)

    def printInfo(self):
        printString = "This is a washing machine "
