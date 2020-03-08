from telegram import ReplyKeyboardMarkup

mainMenuKeyboard = ReplyKeyboardMarkup([['/use', '/status'], ["/info", "/done"], ["/restart"]])

mainMenuAdminKeyboard = ReplyKeyboardMarkup([['/use', '/status'], ["/info", "/done"], ["/config"], ["/restart"]])

startKeyboard = ReplyKeyboardMarkup([['/start']])

# chooseMachineKeyboard = ReplyKeyboardMarkup([['1', '2', '3', '4'],['5', '6', '7', '8'], ['/restart']])

restartKeyboard = ReplyKeyboardMarkup([['/restart']])

machineTypeKeyboard = ReplyKeyboardMarkup([["front"], ["top"]])

adminCommandsKeyboard = ReplyKeyboardMarkup([["/addMachine"], ["/removeMachine"], ["/restart"]])