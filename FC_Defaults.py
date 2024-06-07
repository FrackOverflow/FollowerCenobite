from collections import namedtuple
import json

programData = "ProgramData/"

def InitDefaults(defaultPath = "FC_Defaults.json"):
    defaults = json.load(open(programData + defaultPath))
    keys = list(defaults.keys())
    
    global FcDefaults
    FcDefaults = namedtuple("FcDefaults", keys)

    return FcDefaults(*defaults.values())

def OverwriteDefaults(defaults, defaultPath = "FC_Defaults.json"):
    json.dump(defaults._asdict(), open(programData + defaultPath, "w"))

def InitDict(jsonFileName):
    return json.load(open(programData + jsonFileName))

def OverwriteDict(jsonFileName, dictToWrite):
    return json.dump(dictToWrite, open(programData + jsonFileName, "w"))

if __name__ == "__main__":
    testPath = "TestData/TEST_FC_Defaults.json"
    testDefaults = InitDefaults(testPath)
    newDefaults = testDefaults._replace(ACC_ABBR="TEST WORKING")
    OverwriteDefaults(newDefaults, testPath)