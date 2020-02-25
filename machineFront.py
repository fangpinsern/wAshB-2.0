from datetime import datetime, timedelta

class MachineFront:

    settings = [["Cotton 60 with Prewash", 121], ["Cottons 90", 133], ["Cottons 40", 80], ["Cottons Cold", 80], ["Cottons Eco 60", 132], ["Cottons Eco 40", 120], [
        "Synthetics 60", 113], ["Synthetics 40", 105], ["Synthetics Cold", 66], ["Delicates 30", 65], ["Woolen 40", 54], ["Hand Wash 20", 41], ["Mini 30", 29]]

    settingsKeyboard = [["Cotton 60 with Prewash"], ["Cottons 90"], ["Cottons 40"], ["Cottons Cold"], [
        "Cottons Eco 60"], ["Cottons Eco 40"], ["Synthetics 60"], ["Synthetics 40"], ["Synthetics Cold"], ["Delicates 30"], ["Woolen 40"], ["Hand Wash 20"], ["Mini 30"]]
    inUse = False
    startTime = 0
    endTime = 0
    username = ""
    chatId = 0
    hasReminded = False

    def isInUse(self):
        return self.inUse

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime

    def useMachine(self, username, chatId, setting):
        self.username = username
        self.chatId = chatId
        self.startTime = datetime.now()
        duration = self.getTiming(setting)
        print(duration)
        print(setting)
        self.endTime = self.startTime + timedelta(minutes=duration)
        self.inUse = True

    def doneUse(self):
        self.username = ""
        self.startTime = 0
        self.endTime = 0
        self.chatId = 0
        self.inUse = False

    def getTiming(self, setting):
        time = -1
        for setting1 in self.settings:
            if setting1[0] == setting:
                time = setting1[1]

        return time


