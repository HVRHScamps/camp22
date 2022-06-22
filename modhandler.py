import importlib
import libhousy
import logging
import string
import subprocess
import sys
import time

logging.basicConfig(filename="/var/log/robotmain.log", encoding="utf-8", level=logging.INFO)


class ModHandler:
    def __init__(self, studentmods: list, robot: libhousy.robot):
        """initializes student module subsystem, takes a lits of all modules as an argument"""
        self.falseAutomaton = libhousy.robot(True)
        self.robot = robot
        self.studentModules = studentmods
        self.testStatus = 0
        """0- not running, 1- running, 2-failed requirements, 3-runtime error, 4-pass"""
        self.testStartTime = 0
        self.testStage = 0
        self.runningTests = 0
        # Flag to indicate wheather testing is in progress
        self.mods = {}
        self.modStatus = {}
        self.subject = None
        for mod in self.studentModules:
            sys.path.append("/home/robo/Documents/{}".format(mod))
            self.mods.update({mod: importlib.import_module(mod)})
            self.modStatus.update({mod: False})

    def test_module(self, modulename: string):
        if self.testStatus == 0:
            self.testStartTime = time.time()
            self.runningTests = 1
            self.testStage = 0
            self.testStatus = 1
            self.falseAutomaton = libhousy.robot(True)  # Start with a fresh copy every time
            git = subprocess.Popen(["git", "pull"], cwd="/home/robo/Documents/{}".format(modulename))
            try:
                git.wait(5)
            except subprocess.TimeoutExpired:
                logging.warning("Git pull did not work, using last fetched version")
                pass
            self.subject = self.mods[modulename]
            importlib.reload(self.subject)
        match modulename:
            case "driveForward10":
                match self.testStage:
                    case 0:
                        if self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0:
                            self.testStage += 1
                        elif time.time() - self.testStartTime > 2:
                            logging.error("Did not try to drive forward after 2s. fail.")
                            self.testStatus = 2
                    case 1:
                        if round(time.time() - self.testStartTime, 5) % 2 == 0:
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
                            self.falseAutomaton.lDriveEncoder.value = 6
                    case 1:
                        if self.falseAutomaton.lDrive.value < 0 and self.falseAutomaton.rDrive.value == 0:
                            self.testStage += 1
                            self.falseAutomaton.lDriveEncoder.value = 0
                            self.falseAutomaton.rDriveEncoder.value = 6
                        elif time.time() - self.testStartTime > 3:
                            logging.error("holdStill did not respond correctly to stimulus. Fail!")
                            logging.error("stimulus: ldrive encoder forward 6 in, expected behavior: ldrive reverse, "
                                          "rdrive halt. Acual behavior: ldrive={}, rdrive={}"
                                          .format(self.falseAutomaton.lDrive.value, self.falseAutomaton.rDrive.value))
                            self.testStatus = 2
                            self.modStatus[modulename] = False

                    case 2:
                        if self.falseAutomaton.rDrive.value < 0 and self.falseAutomaton.lDrive.value == 0:
                            self.testStage += 1
                            self.falseAutomaton.lDriveEncoder.value = -6
                            self.falseAutomaton.rDriveEncoder.value = -6
                        elif time.time() - self.testStartTime > 4:
                            logging.error("holdStill did not respond correctly to stimulus. Fail!")
                            logging.error("stimulus: rdrive encoder forward 6 in, expected behavior: rdrive reverse, "
                                          "ldrive halt. Acual behavior: ldrive={}, rdrive={}"
                                          .format(self.falseAutomaton.lDrive.value, self.falseAutomaton.rDrive.value))
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case 3:
                        if self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0:
                            self.testStage += 1
                        elif time.time() - self.testStartTime > 5:
                            logging.error("holdStill did not respond correctly to stimulus. Fail!")
                            logging.error("stimulus: ldrive and rdrive encoders back 6 in, expected behavior: ldrive "
                                          "reverse, rdrive reverse. Acual behavior: ldrive={}, rdrive={}"
                                          .format(self.falseAutomaton.lDrive.value, self.falseAutomaton.rDrive.value))
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "firstSteps":
                match self.testStage:
                    case 0:
                        if time.time() - self.testStartTime > 1:
                            if self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0:
                                self.testStage += 1
                            else:
                                self.testStatus = 2
                                self.modStatus[modulename] = False
                                logging.error("firstSteps Did not move after 5 seconds")
                    case 1:
                        if time.time() - self.testStartTime > 5:
                            if self.falseAutomaton.lDrive.value == 0 and self.falseAutomaton.rDrive.value == 0:
                                self.testStage += 1
                            else:
                                self.testStatus = 2
                                self.modStatus[modulename] = False
                                logging.error("firstSteps kept moving when it shouldn't have")
                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "autoPickup":
                motors = [self.falseAutomaton.pickupMotor, self.falseAutomaton.beltZ1, self.falseAutomaton.beltZ2,
                          self.falseAutomaton.beltZ3]
                pneumatics = [self.falseAutomaton.pickupPneumatic, self.falseAutomaton.upperTension,
                              self.falseAutomaton.lowerTension]
                match self.testStage:
                    case 0:
                        self.testStage += 1  # give the student code 1 loop to get its ducks in a row
                    case 1 | 5:
                        ok = True
                        for m in motors:
                            if m.value != 0:
                                ok = False
                                logging.error("{} was on when it should have been off".format(m.name))
                        if self.falseAutomaton.pickupPneumatic.value != -1:
                            ok = False
                            logging.error("pickup pneumatic should have been retracted")
                        if ok:
                            self.testStage += 1
                        elif time.time() - self.testStartTime > 1:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case 2:
                        self.falseAutomaton.controller.axes[5] = 1
                        self.testStage += 1
                    case 3:
                        if self.falseAutomaton.pickupMotor.value == 1 and self.falseAutomaton.pickupPneumatic.value == 1 \
                                and self.falseAutomaton.beltZ1.value <= -0.8 and self.falseAutomaton.beltZ2.value == 0 \
                                and self.falseAutomaton.beltZ3.value == 0 and self.falseAutomaton.upperTension.value == -1 \
                                and self.falseAutomaton.lowerTension == 1:
                            self.testStage += 1
                        elif time.time() - self.testStartTime > 3:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                            logging.error("one or more actuators was not properly set on trigger pull. Fail.")
                    case 4:
                        self.falseAutomaton.controller.axes[5] = 0
                        self.testStage += 1

                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "gyroTurn":
                match self.testStage:
                    case 0:
                        self.testStage += 1  # give the student code 1 loop to get its ducks in a row
                    case 1: #did it turn in correct direction
                            #left reverse && right forward to turn left OR left still && right forward(i think?)
                        if ((self.falseAutomaton.lDrive.value < 0 and self.falseAutomaton.rDrive.value > 0) 
                            or (self.falseAutomaton.lDrive.value == 0 and self.falseAutomaton.rDrive.value > 0)): 
                            self.testStage += 1
                        elif ((self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value < 0) 
                            or (self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value == 0)): #turned right
                            logging.error("Tried to turn right instead of left")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        elif (((self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0) 
                            or (self.falseAutomaton.lDrive.value < 0 and self.falseAutomaton.rDrive.value < 0))): #drove forward or reverse instead
                            logging.error("Tried to drive instead of turn")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        elif time.time() - self.testStartTime > 2:
                            logging.error("Did not try to turn after 2s. fail.")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case 2: #did it turn the correct amount
                        if self.falseAutomaton.sense_hat.getYaw() == -90: #might need range of accepted values instead of strictly -90??
                            self.testStage += 1
                        elif self.falseAutomaton.sense_hat.getYaw() < -90:
                            logging.error("Turned too far")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        elif self.falseAutomaton.sense_hat.getYaw() > -90:
                            logging.error("Didn't turn far enough")
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case _:   
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests") 
            case _:
                self.testStage += 1
                logging.info("No testing profile defined for module, running stability-only test")
                if self.testStage == 25:
                    self.testStatus = 4
                    self.modStatus[modulename] = True  # assume true until the except below proves otherwise
        try:
            self.subject.main(self.falseAutomaton)
        except Exception as err:
            logging.error("Testing student module failed due to {}".format(err))
            self.modStatus[modulename] = False
            return 3
        return self.testStatus

    def run_module(self, modulename: string):
        if self.testStatus == 0:
            importlib.reload(self.subject)
            self.testStatus = 1
        """Returns: 0 - running, 1 - internal fault 2 - done"""
        self.subject = self.mods[modulename]
        try:
            if self.subject.main(self.robot) == 2:
                return 2
        except Exception as err:
            logging.error("Running student module failed due to {}".format(err))
            self.modStatus[modulename] = False
            return 1
        return 0

    def reset(self):
        self.testStatus = 0
        self.testStage = 0
        self.testStartTime = 0
        self.runningTests = 0
