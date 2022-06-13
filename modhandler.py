import importlib
import libhousy
import string
import time
import logging


class modhandler:
    def __init__(self, studentmods: list, robot: libhousy.robot):
        """initializes student module subsystem, takes a lits of all modules as an argument"""
        self.falseAutomaton = libhousy.robot(True)
        self.robot = robot
        self.studentModules = studentmods
        self.testStatus = 0
        # 0- not running, 1- running, 2-failed requirements, 3-runtime error, 4-pass
        self.testStartTime = 0
        self.testStage = 0
        self.runningTests = 0
        # Flag to indicate wheather testing is in progress
        self.mods = {}
        self.modStatus = {}
        for mod in self.studentModules:
            self.mods.update({mod: importlib.import_module(mod)})
            self.modStatus.update({mod: False})

    def testModule(self, modulename: string):
        if self.testStatus == 0:
            self.testStartTime = time.time()
            self.runningTests = 1
            self.testStage = 0
        subject = self.mods[modulename]
        importlib.reload(subject)
        match modulename:
            case "driveforward10":
                match self.testStage:
                    case 0:
                        if self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0:
                            self.testStage += 1
                        elif time.time() - self.testStartTime > 2:
                            logging.error("Did not try to drive forward after 2s. fail.")
                            self.testStatus = 2
                    case 1:
                        if round(time.time()-self.testStartTime, 5) % 2 == 0:
                            # 16ft/s * 12in/ft * 2s/tick * throttle input
                            # This won't be super accurate bc the drivetrain isn't exactly 16ft/s and speed does not
                            # scale linearly with throttle input but whatever
                            self.falseAutomaton.lDriveEncoder.value += self.falseAutomaton.lDrive.value * 192 * 2
                            self.falseAutomaton.rDriveEncoder.value += self.falseAutomaton.rDrive.value * 192 * 2
                        if abs(self.falseAutomaton.lDriveEncoder.value - self.falseAutomaton.rDriveEncoder.value) > 4:
                            logging.error("turned when it shouldn't")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        if abs(120 - self.falseAutomaton.lDriveEncoder.Get()) < 4:
                            self.testStage += 1
                        elif self.falseAutomaton.lDriveEncoder.Get() > 124:
                            # safe to only use left drive encoder here since above we ensure they are roughly equal
                            logging.error("overshot target")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        elif time.time() - self.testStartTime > 10:
                            logging.error("took too long!")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case _:
                        # since we're out of bounds, assume success due to pass case addition
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "holdStill":
                match self.testStage:
                    case 0:
                        self.falseAutomaton.lDriveEncoder.value = 0
                        self.falseAutomaton.rDriveEncoder.value = 0
                        if self.falseAutomaton.lDrive.value != 0 or self.falseAutomaton.rDrive.value != 0:
                            self.testStatus = 2
                            logging.error("moved uncommanded")
                        elif time.time() - self.testStartTime > 2:
                            self.testStage += 1
                            self.falseAutomaton.lDriveEncoder.value = 50
                    case 1:
                        if self.falseAutomaton.lDrive.value < 0 and self.falseAutomaton.rDrive.value == 0:
                            self.testStage += 1
                            self.falseAutomaton.lDriveEncoder.value = 0
                            self.falseAutomaton.rDriveEncoder.value = 50
                    case 2:
                        if self.falseAutomaton.rDrive.value < 0 and self.falseAutomaton.lDrive.value == 0:
                            self.testStage += 1
                            self.falseAutomaton.lDriveEncoder.value = -50
                            self.falseAutomaton.rDriveEncoder.value = -50
                    case 3:
                        if self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0:
                            self.testStage += 1
                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case _:
                logging.warning("No testing profile defined for module")
                logging.warning("running stability-only test")
                self.modStatus[modulename] = True  # assume true until the except below proves otherwise
        try:
            subject.main(self.falseAutomaton)
        except:
            self.modStatus[modulename] = False
            return 3
        return self.testStatus

    def runModule(self, modulename: string):
        """Returns: 0 - running, 1 - internal fault"""
        subject = self.mods[modulename]
        importlib.reload(subject)
        try:
            subject.main(self.robot)
        except:
            return 1
        return 0
