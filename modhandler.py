import importlib
import libhousy
import logging
import string
import subprocess
import sys
import time

logging.basicConfig(filename="/var/log/robotmain.log", encoding="utf-8", level=logging.WARNING)


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
                            self.testStage += 2
                        elif time.time() - self.testStartTime > 2:
                            logging.error("Did not try to drive forward after 2s. fail.")
                            self.testStatus = 2
                    case 1:
                        tmp = (round(time.time() - self.testStartTime, 5) - round(time.time() - self.testStartTime, 0))
                        if tmp == 0 or tmp == 0.5:
                            # 16ft/s * 12in/ft * 0.5s/tick * throttle input
                            # 16ft/s * 12in/ft * 0.5s/tick * throttle input
                            # This won't be super accurate bc the drivetrain isn't exactly 16ft/s and speed does not
                            # scale linearly with throttle input but whatever
                            self.falseAutomaton.lDriveEncoder.value += self.falseAutomaton.lDrive.value * 192 * .5
                            self.falseAutomaton.rDriveEncoder.value += self.falseAutomaton.rDrive.value * 192 * .5
                            logging.info("lDriveEncoder: {}".format(self.falseAutomaton.lDriveEncoder.Get()))
                            logging.info("rDriveEncoder: {}".format(self.falseAutomaton.rDriveEncoder.Get()))
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
                        else:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                    case 2:
                        self.falseAutomaton.controller.axes[5] = 1
                        self.testStage += 1
                    case 3:
                        if self.falseAutomaton.pickupMotor.value == 1 and self.falseAutomaton.pickupPneumatic.value == 1 \
                                and self.falseAutomaton.beltZ1.value <= -0.8 and self.falseAutomaton.beltZ2.value == 0 \
                                and self.falseAutomaton.beltZ3.value == 0 and self.falseAutomaton.upperTension.value == -1 \
                                and self.falseAutomaton.lowerTension.value == 1:
                            self.testStage += 1
                        else:
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

            case "manualLaunch":
                motors = [self.falseAutomaton.shootWheel, self.falseAutomaton.beltZ1, self.falseAutomaton.beltZ2,
                          self.falseAutomaton.beltZ3]
                match self.testStage:
                    case 0:
                        self.testStage += 1  # give the student code 1 loop to get its ducks in a row
                    case 1 | 3:
                        ok = True
                        for m in motors:
                            if m.value != 0:
                                ok = False
                                logging.error("{} was on when it should have been off".format(m.name))
                        if ok:
                            self.testStage += 1
                        else:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                            if self.testStage == 3:
                                logging.error("Tried to shoot when shoot wheel was not spun up!")
                    case 2:
                        self.falseAutomaton.controller.axes[4] = 1
                        self.testStage += 1
                    case 4:
                        self.falseAutomaton.controller.axes[4] = 0
                        self.falseAutomaton.controller.buttons[7] = True
                        self.testStage += 1
                    case 5:
                        ok = True
                        for m in motors[1:4]:
                            if m.value != 0:
                                ok = False
                                logging.error("{} was on when it should have been off".format(m.name))
                        if ok and self.falseAutomaton.shootWheel.value > 0.8:
                            self.testStage += 1
                        else:
                            logging.error("Bad spin up!")
                    case 6:
                        self.falseAutomaton.controller.axes[4] = 1
                        self.falseAutomaton.controller.buttons[7] = True
                        self.testStage += 1
                    case 7:
                        if self.falseAutomaton.beltZ1.value <= -0.8 and self.falseAutomaton.beltZ2.value <= -0.8 \
                                and self.falseAutomaton.beltZ3.value == 1 and self.falseAutomaton.upperTension.value == 1 \
                                and self.falseAutomaton.lowerTension.value == -1 and self.falseAutomaton.shootWheel.value > 0.8:
                            self.testStage += 1
                        else:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                            logging.error("Belt system did not respond properly during launch sequence. Fail.")
                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "autoLaunch":
                motors = [self.falseAutomaton.beltZ1, self.falseAutomaton.beltZ2,
                          self.falseAutomaton.beltZ3]
                tmp = (round(time.time() - self.testStartTime, 5) - round(time.time() - self.testStartTime, 0))
                match self.testStage:
                    case 0:
                        self.testStage += 1  # give the student code 1 loop to get its ducks in a row
                    case 1:
                        ok = True
                        for m in motors:
                            if m.value != 0:
                                ok = False
                                logging.error("{} was on when it should have been off".format(m.name))
                        if ok:
                            self.testStage += 1
                        else:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                            if self.testStage == 3:
                                logging.error("Tried to shoot when shoot wheel was not spun up!")
                    case 2:
                        if self.falseAutomaton.shootWheel.value != 0:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                            logging.error("Shoot wheel uncommanded spin up")
                        self.falseAutomaton.controller.axes[4] = 1
                        self.testStage += 1
                    case 3 | 4 | 5 | 6 | 7:
                        ok = True
                        if self.falseAutomaton.shootWheel.value == 0:
                            ok = False
                            logging.error("Shoot wheel did not turn on when it should.")
                        if self.falseAutomaton.beltZ1.value != 0 or self.falseAutomaton.beltZ2.value != 0 or \
                                self.falseAutomaton.beltZ3.value != 0:
                            ok = False
                            logging.error("Belts moved when they shouldn't")
                        if not ok:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        elif tmp == 0 or tmp == 0.5:
                            self.testStage += 1
                            self.falseAutomaton.shootEncoder.value += 125 * self.testStage
                    case 8:
                        ok = True
                        if tmp == 0 or tmp == 0.5:
                            self.testStage += 1
                            self.falseAutomaton.shootEncoder.value += 65 * self.testStage
                        if self.falseAutomaton.beltZ1.value > -0.8 or self.falseAutomaton.beltZ2.value > -0.8 \
                                or self.falseAutomaton.beltZ3.value != 1 or self.falseAutomaton.upperTension.value != 1 \
                                or self.falseAutomaton.lowerTension != -1 or self.falseAutomaton.shootWheel.value < 0.8:
                            ok = False
                            logging.error("Belt system did not respond correctly to spin up.")
                        if not ok:
                            self.testStatus = 2
                            self.modStatus[modulename] = False
                        else:
                            self.testStage += 1
                    case _:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")

            case "gyroTurn":
                turnrate = (self.falseAutomaton.lDrive.value - self.falseAutomaton.rDrive.value) / 2
                self.falseAutomaton.sense_hat.yaw += turnrate * 5
                if self.falseAutomaton.sense_hat.get_yaw() < -92:
                    logging.warning("gyroTurn overshoot. Angle={}".format(self.falseAutomaton.sense_hat.get_yaw()))
                    self.testStage = 0
                elif self.falseAutomaton.sense_hat.get_yaw() < -88:
                    self.testStage += 1
                else:
                    self.testStage = 0
                if self.testStage >= 20:
                    if abs(turnrate) < 0.1:
                        self.testStatus = 4
                        self.modStatus[modulename] = True
                        logging.info("passed all tests")
                    else:
                        logging.error("Turned succussfully but appears to be twitching. Try loosening tolerances or PID")
                        self.testStatus = 2
                        self.modStatus[modulename] = False
                elif time.time() - self.testStartTime > 5:
                    self.testStatus = 2
                    self.modStatus[modulename] = False
                    logging.error("Did not turn in time. Final angle: {} lDrive: {} rDrive: {}"
                                  .format(self.falseAutomaton.sense_hat.get_yaw(), self.falseAutomaton.lDrive.value(),
                                          self.falseAutomaton.rDrive.value()))
            case "verbalNav":
                self.testStatus = 4
                self.modStatus[modulename] = True  # assume true until the except below proves otherwise
                return self.testStatus
            case _:
                match self.testStage:
                    case 0:
                        logging.info("{} cannot be fully tested, checking stability only...".format(modulename))
                    case 25:
                        self.testStatus = 4
                        self.modStatus[modulename] = True  # assume true until the except below proves otherwise
                self.testStage += 1

        try:
            self.subject.main(self.falseAutomaton)
        except Exception as err:
            logging.error("Testing student module failed due to {}".format(err))
            self.modStatus[modulename] = False
            return 3
        return self.testStatus

    def run_module(self, modulename: string):
        if self.testStatus == 0:
            self.subject = self.mods[modulename]
            importlib.reload(self.subject)
            self.testStatus = 1
            self.robot.control.putNumber("encRst", 5)  # reset navx
            while self.robot.control.getNumber("encRst", 1) != 0:
                time.sleep(0.05)  # wait for robo rio ack
            self.robot.control.putNumber("encRst", 6)  # reset both drivetrain encoders
            while self.robot.control.getNumber("encRst", 1) != 0:
                time.sleep(0.05)  # wait for robo rio ack
        """Returns: 0 - running, 1 - internal fault 2 - done"""
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
