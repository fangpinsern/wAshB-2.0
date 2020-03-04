import pickle
import os

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
                machinesUsedByUser.append([str(counter)])
            counter = counter + 1
        return machinesUsedByUser

    def getMachinesInUse(self):
        machinesInUse = []
        for machine in self.machinesArr:
            if machine.isInUse():
                machinesInUse.append(machine)
        return machinesInUse

    def useMachine(self, index, username, chatId, setting):
        validUse = self.machinesArr[index - 1].useMachine(username, chatId, setting)
        self.onChange()
        return validUse

    def doneUse(self, index, chatId):
        validDoneUse = self.machinesArr[index - 1].doneUse(chatId)
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