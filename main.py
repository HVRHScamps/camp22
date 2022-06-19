import logging
from enum import Enum
import libhousy
import time
import pygame
import yaml
from modhandler import modhandler
import display
from teleop import Teleop

robot = libhousy.robot()
Mods = modhandler(
    ["firstSteps", "driveForward10", "autoPickup", "manualLaunch", "autoLaunch", "gyroTurn", "holdStill", "getHome",
     "verbalNav", "teleop"],
    robot)
screen = display.Display()
controller = libhousy.controller()
to = Teleop(robot)
logging.basicConfig(filename="/var/log/robotmain.log", encoding="utf-8", level=logging.INFO)
intro_flag = True
do_die_pygame = False
with open('persist.yaml', "r") as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)
    if data["modstat"] is not None:
        Mods.modStatus = data["modstat"]
    if data["intro_flag"] is not None:
        intro_flag = data["intro_flag"]
update_timer = time.time()
pygame_death_timer = time.time()


class RobotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3


class leds:
    dead_flag = False
    dead_timer = 0

    def run(self, override=None, status=None):
        match override:
            case "dead":
                self.dead_flag = True
                self.dead_timer = time.time()
                robot.sensors.putString("display", "dead")
            case None:
                if self.dead_flag:
                    self.dead_flag = not (time.time() - self.dead_timer > 10)
                else:
                    if status is not None:
                        ok = 0
                        for i in status:
                            if status[i]:
                                ok += 1
                        match ok:
                            case 0 | 1:
                                robot.sensors.putString("display", "sad1")
                            case 2 | 3:
                                robot.sensors.putString("display", "sad2")
                            case 4 | 5 | 6:
                                robot.sensors.putString("display", "neutral")
                            case 7 | 8:
                                robot.sensors.putString("display", "happy1")
                            case 9 | 10:
                                robot.sensors.putString("display", "happy2")
            case Default:
                robot.sensors.putString("display", override)


curState = RobotState.stopped
curMod = [Mods.studentModules[0], 0]
hat = leds()


def teleop():
    to.drive(controller.getAxis(controller.Axis.rStickX), controller.getAxis(controller.Axis.rStickY))
    robot.shootWheel.Set(int(controller.getButton(controller.Button.rBumper)))
    if controller.getAxis(controller.Axis.lTrigger) > 0.8:
        to.pickup()
    elif controller.getAxis(controller.Axis.rTrigger) > 0.8 and controller.getButton(controller.Button.rBumper):
        to.shoot()
    else:
        to.stop()
    to.anglehood(controller.getAxis(controller.Axis.lStickY))
    time.sleep(0.01)


def set_mod(num):
    global curMod
    curMod = [Mods.studentModules[num], num]
    screen.select_box(num)


while True:
    if intro_flag:
        screen.intro()
    else:
        screen.run(Mods.studentModules, Mods.modStatus)
    if curState != RobotState.stopped:
        robot.keepAlive()
        robot.control.putBoolean("stop", False)
    match curState:
        case RobotState.stopped:
            if do_die_pygame:
                tm = time.time() - pygame_death_timer
                screen.die(tm)
                if tm > 10:
                    do_die_pygame = False
            if time.time() - update_timer > 120:
                to_write = {"modstat": Mods.modStatus, "intro_flag": intro_flag}
                with open('persist.yaml', 'w') as f:
                    data = yaml.dump(to_write, f)
                update_timer = time.time()
            logging.debug("robot stopped")
            robot.control.putBoolean("stop", True)
            hat.run(status=Mods.modStatus)
            Mods.reset()
            for event in pygame.event.get():
                match event.type:
                    case pygame.JOYHATMOTION:
                        match event.value:
                            case (1, 0) | (-1, 0):
                                if curMod[1] < 5:
                                    newMod = curMod[1] + 5
                                else:
                                    newMod = curMod[1] - 5
                            case (0, -1):
                                newMod = curMod[1] + 1
                                if newMod > 9:
                                    newMod = curMod[1]
                            case (0, 1):
                                newMod = curMod[1] - 1
                                if newMod < 0:
                                    newMod = 9
                            case default:
                                newMod = curMod[1]
                        set_mod(newMod)
                        logging.debug("Curmod: {}".format(curMod))
                    case pygame.JOYBUTTONDOWN:
                        if controller.getButton(controller.Button.A):
                            curState = RobotState.testing
                        if controller.getButton(controller.Button.hamburger):
                            curState = RobotState.teleop
                            to.switchback = False
                        if controller.getButton(controller.Button.Y):
                            curState = RobotState.running

        case RobotState.teleop:
            if intro_flag:
                hat.run(override="happy2")
                logging.debug("teleop mode")
                teleop()
                if controller.getButton(controller.Button.B):
                    curState = RobotState.stopped
                if controller.getButton(controller.Button.lStick) and controller.getButton(controller.Button.save):
                    curState = RobotState.stopped
                    intro_flag = False
                    do_die_pygame = True
                    pygame_death_timer = time.time()
                    hat.run(override="dead")

        case RobotState.testing:
            hat.run(override="thinking")
            logging.info("testing student code...")
            match Mods.testModule(curMod[0]):
                case 4:
                    curState = RobotState.stopped
                    logging.info("Module {} passed all test!".format(curMod[0]))
                case (0 | 1):
                    curState = RobotState.testing
                case _:
                    curState = RobotState.stopped
                    logging.error("Student code failed its tests!")
                    hat.run(override="dead")
            if time.time() - Mods.testStartTime > 45:
                logging.error("Test overran allotted time. Fail.")
                Mods.modStatus.update({curMod[0]: False})
                curState = RobotState.stopped
                hat.run(override="dead")
        case RobotState.running:
            hat.run(override="running")
            logging.debug("running student code")
            if not Mods.modStatus[curMod[0]]:  # makes sure module passed its last test
                logging.warning("Module {} has not passed its tests and cannot be run. Abort.".format(curMod[0]))
                curState = RobotState.stopped
                continue
            match Mods.runModule(curMod[0]):
                case 0:
                    continue
                case 1:
                    curState = RobotState.stopped
                    logging.error("Student code crashed!")
                    hat.run(override="dead")
                    Mods.modStatus.update(curMod[0], False)  # make note of failure
                case 2:
                    curState = RobotState.stopped
                    logging.info("Student code exited gracefully")
            for event in pygame.event.get():
                if event.type == pygame.CONTROLLERBUTTONDOWN:
                    curState = RobotState.stopped
                    print("stop requested by xbox controller")
