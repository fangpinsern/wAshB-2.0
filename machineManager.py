class MachineManager:

    machinesArr=[]

    #addMachine
    #removeMachine
    #getNextAvailableTime: return which machine is available and what time
    #getMachine: returns the machine being chosens
    #printstatus: return the status of the machines under management
    #sendreminder: sends reminder to the person

    def __init__(self, machinesArr):
        self.machinesArr = machinesArr

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