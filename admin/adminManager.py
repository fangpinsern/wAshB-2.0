from telegram import ReplyKeyboardMarkup

class AdminManager:
    """
    A class used to represent a manger for admins.

    ...

    Attributes
    ----------
    adminArr : list
        list of all the people that are admin
    master: integer
        the master user which has the admin rights to the admins

    Methods
    -------
    isMaster(masterId)
        returns True if masterId is the master ID
    addAdmin(username)
        adds username to the list of admins
    removeAdmin(username)
        removes admin from the list of admins
    getAdminKeyboard()
        give the ReplyKeyboardMarkup of the list of admins
    getListOfAdmins()
        return a string with information of who is an admin
    adminIdExist(username)
        chaecks if the username is in the admin manager
    """
    adminArr = []
    master = 0
    
    def __init__(self, firstAdmin):
        self.adminArr.append(firstAdmin)
        self.master = firstAdmin
    
    def isMaster(self, masterId):
        return self.master == masterId

    ## master functions
    def addAdmin(self, username):
        validAdmin = False
        if not self.adminIdExist(username):
            self.adminArr.append(username)
            validAdmin = True
        return validAdmin

    def removeAdmin(self, username):
        validRemove = False
        if self.adminIdExist(username):
            self.adminArr.remove(username)
            validRemove = True
        return validRemove

    def getAdminKeyboard(self):
        mainKeyboard = []
        count = 0
        for admin in self.adminArr:
            if count==0:
                count = count + 1
                continue
            mainKeyboard.append([admin])
            count = count + 1
        return ReplyKeyboardMarkup(mainKeyboard)

    def getListOfAdmins(self):
        listOfAdmins =""
        count = 0
        for admin in self.adminArr:
            if count == 0:
                listOfAdmins = listOfAdmins + "Master: {}\n".format(self.master)
                count = count + 1
            else:
                listOfAdmins = listOfAdmins + "{}. {}\n".format(count, admin)
                count = count + 1

        return listOfAdmins

    ## adminFunctions
    def adminIdExist(self, username):
        return username in self.adminArr
    



        