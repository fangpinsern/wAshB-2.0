import unittest

from machineFront.machineFront import MachineFront

testMachineFront = MachineFront("front")

class TestSum(unittest.TestCase):
    def test_settingExist_valid(self):
        #Test whether check for existence of setting exist
        setting = testMachineFront.settings[0][0]
        result = testMachineFront.checkSettingExist(setting)
        self.assertEqual(result, True)

    def test_settingExist_invalid(self):
        invalidSetting = "abc"
        result = testMachineFront.checkSettingExist(invalidSetting)
        self.assertEqual(result, False)


if __name__ == "__main__":
    unittest.main()
