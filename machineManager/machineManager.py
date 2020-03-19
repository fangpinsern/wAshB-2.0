import pickle
import os
import math

from telegram import ReplyKeyboardMarkup

class MachineManager:

    """
    A class used to represent a MachineManager.

    ...

    Attributes
    ----------
    machineArr : list
        a list of machines that are managed by this manager
    bannedUsers : list
        a list of users that are banned from using machines managed by this manager
    filename : str
        name of the file that will save the information of the machineManager

    Methods
    -------
    getMachineByName(name)
        gets the machine instance with the name provided in the parameter
    printStatus()
        Prints the status of all the machines being managed by this manager
    getMachineUsedByUser(chatId)
        gives a list of machines that are being used by the user with the 
        given chatId
    getMachinesInUse()
        gives a list of the machines that are in use
    nameExist(name)
        checks if the name given in the parameter exists in the machines 
        managed by this manager
    useMachine(name, username, chatId, setting)
        to use the machine with the name given in the parameter
    doneUse(name, chatId)
        signals manager that user with chatId has finished using the machine 
        with the name in the parameter
    isAllInUse()
        returns True what all the machines in the manager is used
        else, returns False
    getKeyboard() 
        returns the KeyboardMarkUp with the names of the machines
    getMachineUsedByUserKeyboard(chatId)
        returns KeyboardMarkUp with the names of machines used
        by the chatId in parameters
    addMachine(machine)
        adds machine to be managed by the manager
    removeMachineByName(machineName)
        removes machine from being managed by manager
    banUser(username)
        add user to the bannedUsers list
    isBannedUser(username)
        returns True if the user is in the banned list
        else returns False
    getBannedUserString()
        gives a formatted string of users that are banned
    """

    machinesArr = []
    bannedUsers = []
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

    def getMachineByName(self, name):
        returnMachine = False
        for machine in self.machinesArr:
            if machine.getName() == name:
                return machine
        return returnMachine

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

    def useMachine(self, name, username, chatId, setting):
        machine = self.getMachineByName(name)
        validUse = machine.useMachine(username, chatId, setting)
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
        numberOfPairs = math.ceil((len(self.machinesArr))/2)
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
                keyboardMain[rowCount].append(machine.getName())
                count = 1

        keyboardMain.append(['/restart'])
        return ReplyKeyboardMarkup(keyboardMain)

    def getMachineUsedByUserKeyboard(self, chatId):
        keyboardMain = self.getMachineUsedByUser(chatId)

        keyboardMain.append(["/restart"])

        return ReplyKeyboardMarkup(keyboardMain)


    def addMachine(self, machine):
        # name has to be unique
        validAddMachine = False
        if not self.nameExist(machine.getName()):
            self.machinesArr.append(machine)
            self.onChange()
            validAddMachine=True

        return validAddMachine

    def removeMachineByName(self, machineName):
        validRemoveMachine = False
        if self.nameExist(machineName):
            for machine in self.machinesArr:
                if machineName == machine.getName():
                    self.machinesArr.remove(machine)
                    validRemoveMachine = True
                    break

        self.onChange()
        return validRemoveMachine

    def banUser(self, username):
        self.bannedUsers.append(username)

    def isBannedUser(self, username):
        return username in self.bannedUsers

    def getBannedUserString(self):
        if len(self.bannedUsers) == 0:
            return "No one is banned at the moment"
        else:     
            s = ""
            count = 1
            for user in self.bannedUsers:
                s = s + "{}. {}\n".format(str(count), user)
                count = count + 1
            return s

        

