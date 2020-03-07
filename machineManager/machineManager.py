import pickle
import os
import math

from telegram import ReplyKeyboardMarkup

class MachineManager:

    machinesArr=[]
    filename = ""

    #addMachine
    #removeMachine
    #getNextAvailableTime: return which machine is available and what time
    #getMachine: returns the machine being chosens
    #printstatus: return the status of the machines under management
    #sendreminder: sends reminder to the person

    def __init__(self, machinesArr, filename):
        self.machinesArr = machinesArr
        self.filename = filename
        if not os.path.isfile(filename):
            print("File dont exist")
            self.storeMachineManager()
        self.retrieveMachineManger()


    def getMachine(self, index):
        return self.machinesArr[index - 1]

    def printStatus(self):
        status = ""
        machineNum = 1
        for machine in self.machinesArr:
            status = status + machine.printStatus(machineNum)
            machineNum = machineNum + 1
        return status

    def getMachineUsedByUser(self, chatId):
        machinesUsedByUser = []
        counter = 1
        for machine in self.machinesArr:
            if machine.getChatId() == chatId:
                machinesUsedByUser.append([machine.getName()])
            counter = counter + 1
        return machinesUsedByUser

    def getMachinesInUse(self):
        machinesInUse = []
        for machine in self.machinesArr:
            if machine.isInUse():
                machinesInUse.append(machine)
        return machinesInUse

    def nameExist(self, name):
        nameExist = False
        for machine in self.machinesArr:
            if machine.getName() == name:
                nameExist = True
        return nameExist

    def useMachine(self, index, username, chatId, setting):
        validUse = self.machinesArr[index - 1].useMachine(username, chatId, setting)
        self.onChange()
        return validUse

    def doneUse(self, name, chatId):
        validDoneUse = False
        for machine in self.machinesArr:
            if machine.getName() == name:
                machine.doneUse(chatId)
                validDoneUse = True
                break
        if validDoneUse:
            self.onChange()
        return validDoneUse

    def isAllInUse(self):
        allInUse = True
        for machine in self.machinesArr:
            allInUse = allInUse and machine.isInUse()
        return allInUse

    def storeMachineManager(self):
        pickle_out = open(self.filename, "wb")
        pickle.dump(self.machinesArr, pickle_out)
        print("storing session")
        pickle_out.close()

    def retrieveMachineManger(self):
        pickle_in = open(self.filename, "rb")
        self.machinesArr = pickle.load(pickle_in)
        print("retrieving session")
        return True

    def onChange(self):
        self.storeMachineManager()

    def getKeyboard(self):
        keyboardMain = []
        numberOfPairs = math.ceil(len(self.machinesArr)/2)
        for i in range(numberOfPairs):
            keyboardMain.append([])
        rowCount = 0
        count = 0
        for machine in self.machinesArr:
            if count < 2:
                keyboardMain[rowCount].append(machine.getName())
                count = count + 1
            else:
                rowCount = rowCount + 1
                count = 0

        keyboardMain.append(['/restart'])
        return ReplyKeyboardMarkup(keyboardMain)

    def getMachineUsedByUserKeyboard(self, chatId):
        keyboardMain = self.getMachineUsedByUser(chatId)

        keyboardMain.append(["/restart"])

        return ReplyKeyboardMarkup(keyboardMain)

