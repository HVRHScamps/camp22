import importlib
import fakerobot
import string
falseAutomaton = fakerobot.robot()
studentModules = ["testme"]
mods = {}
for mod in studentModules:
    mods.update({mod:importlib.import_module(mod)})

def testModule(modulename: string):
    subject = mods[modulename]
    importlib.reload(subject)
    try:
        subject.main()
    except:
        return 1
    return 0