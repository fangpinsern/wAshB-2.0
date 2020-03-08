import unittest

from machineFront.machineFront import MachineFront

class TestSum(unittest.TestCase):
    def test_settingExist_valid(self):
        #Test whether check for existence of setting exist
        testMachineFront = MachineFront("front", "1")
        setting = testMachineFront.settings[0][0]
        result = testMachineFront.checkSettingExist(setting)
        self.assertEqual(result, True)

    def test_settingExist_invalid(self):
        testMachineFront = MachineFront("front", "1")
        invalidSetting = "abc"
        result = testMachineFront.checkSettingExist(invalidSetting)
        self.assertEqual(result, False)

    def test_useMachine_valid(self):
        testMachineFront = MachineFront("front", "1")
        username = "pins"
        chatId = 123
        setting = testMachineFront.settingsKeyboard[0][0]
        validUse = testMachineFront.useMachine(username, chatId, setting)
        self.assertEqual(validUse, True)
    
    def test_useMachine_invalid(self):
        testMachineFront = MachineFront("front", "1")
        username = "pins"
        chatId = 123
        setting = "Invalid Setting"
        invalidUse = testMachineFront.useMachine(username, chatId, setting)
        self.assertEqual(invalidUse, False)

    
if __name__ == "__main__":
    unittest.main()
