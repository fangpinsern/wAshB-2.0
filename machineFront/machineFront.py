from datetime import datetime, timedelta

class MachineFront:
    """
    A class used to represent a Machine.

    ...

    Attributes
    ----------
    name: str
        name of the machine
    inUse: boolean
        true if the machine is use
        false if th machine is not in use
    startTime: dateTime
        time that the machine start to be used
        default is 0 if unused
    endTime: dateTime
        time which the machine should be done with use
        default is 0 if unused
    username: str
        username of user using the machine
        empty string if the machine is left unused
    chatId: int
        chatId of the user using the machine.
        0 if machine is unused
    hasReminded: boolean
        true if the user of the machine has already been reminded that the
        time is up
        else false
    typeOfMachine: str
        what machine type is it
    settings : list
        a list setting for the machine and their corresponding timings
        format: [name_of_setting, duration]
    settingsKeyboard: list
        keyboard that contains the setting of the machine
    infoMessage: str
        information about the machine

    Methods
    -------
    isInUser()
        returns true if the machine is in use
        else return false
    getStartTime()
        gets the start time of usage of machine 
    getEndTime()
        gets the end time of the usage of the machine
    getInfoMessage()
        gets the infomation message of the machine
    getChatId()
        gets the chatId of the person using the machine
    getName()
        gets the name of the machine
    useMachine(username, chatId, setting)
        change status of inUse from False to True
    doneUse(chatId)
        change status of inUse from True to False provided
        that the chatId is the chatId using the machine
    getTimeing(setting)
        get the timing of the setting that is chosen
    checkSettingExist(setting)
        returns True if setting exists
        else False
    printStatus()
        returns a string describing the status of the machine currently
    """

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

    name = "default"
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

    def __init__(self, typeOfMachine, name):
        self.typeOfMachine = typeOfMachine
        self.name = name
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

    def getName(self):
        return self.name

    def useMachine(self, username, chatId, setting):
        validUse = False
        duration = self.getTiming(setting)
        if (self.checkSettingExist(setting)):
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

    def checkSettingExist(self, setting):
        settingExist = False
        for setting1 in self.settings:
            if setting1[0] == setting:
                settingExist = True
                break
        return settingExist
    
    def printStatus(self, id):
        if (self.inUse):
            return "Machine {} is in use. Available after {}\n".format(self.name, self.endTime.strftime("%H:%M:%S"))
        else:
            return "Machine {} is available.\n".format(self.name)

    def printInfo(self):
        printString = "This is a washing machine "
