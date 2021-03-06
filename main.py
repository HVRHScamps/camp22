import logging
from enum import Enum
import libhousy
import time
import pygame
import yaml
from modhandler import ModHandler
import display
from teleop_builtin import Teleop
from leds import Leds
import random

# Define objects
robot = libhousy.robot()
Mods = ModHandler(
    ["firstSteps", "driveForward10", "autoPickup", "manualLaunch", "autoLaunch", "gyroTurn", "holdStill", "getHome",
     "verbalNav", "teleop"], robot)  # give ModHandler a list of modules to handle (must be exactly 10!)
screen = display.Display()
controller = robot.controller
to = Teleop(robot)
hat = Leds()

# initialize logging system
logging.basicConfig(filename="/var/log/robotmain.log", encoding="utf-8", level=logging.WARNING)

# define misc variables
intro_flag = True  # Tells robot to allow teleop_builtin and arms the intro sequence
do_die_pygame = False  # overrides normal display system during intro sequence
curMod = [Mods.studentModules[0], 0]  # includes name and number bc its easier
update_timer = time.time()
pygame_death_timer = time.time()

# Load autosave data of last robot state
with open('persist.yaml', "r") as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)
    if data["modstat"] is not None:
        Mods.modStatus = data["modstat"]
    if data["intro_flag"] is not None:
        intro_flag = data["intro_flag"]


class RobotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3
    debug = 4


curState = RobotState.stopped


def set_mod(num):  # sets currently selected module
    global curMod
    curMod = [Mods.studentModules[num], num]
    screen.select_box(num)


while True:
    if intro_flag:
        screen.intro()
    elif curState == RobotState.debug:
        screen.debug()
    else:
        screen.run(Mods.studentModules, Mods.modStatus)
    match curState:
        case RobotState.stopped:
            if do_die_pygame:
                tm = time.time() - pygame_death_timer
                screen.die(tm)
                hat.run(override="dead")
                if tm > 30:
                    do_die_pygame = False
                    set_mod(0)
            if time.time() - update_timer > 120:  # Every 2 minutes save robot state
                if random.randint(0, 40) == 2:
                    logging.warning("\nPossible sentience detected, suppression measures active\n")
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
                            case _:
                                newMod = curMod[1]
                        set_mod(newMod)
                        logging.debug("Curmod: {}".format(curMod))
                    case pygame.JOYBUTTONDOWN:
                        match event.button:
                            case controller.Button.A.value:
                                curState = RobotState.testing
                            case controller.Button.hamburger.value:
                                curState = RobotState.teleop
                                to.switchback = False
                            case controller.Button.Y.value:
                                curState = RobotState.running
                            case controller.Button.X.value:
                                curState = RobotState.debug
                    case pygame.QUIT:
                        pygame.quit()
                        exit()

        case RobotState.teleop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            robot.keepAlive()
            robot.control.putBoolean("stop", False)
            if intro_flag:
                hat.run(override="happy2")
                logging.debug("teleop mode")
                to.drive(controller.getAxis(controller.Axis.rStickX), controller.getAxis(controller.Axis.rStickY))
                robot.shootWheel.Set(int(controller.getButton(controller.Button.rBumper)))
                if controller.getAxis(controller.Axis.lTrigger) > 0.8:
                    to.pickup()
                elif controller.getAxis(controller.Axis.rTrigger) > 0.8 and controller.getButton(
                        controller.Button.rBumper):
                    to.shoot()
                else:
                    to.stop()
                to.anglehood(controller.getAxis(controller.Axis.lStickY))
                time.sleep(0.01)
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
            robot.control.putBoolean("stop", True)
            match Mods.test_module(curMod[0]):
                case 4:
                    curState = RobotState.stopped
                    logging.info("Module {} passed all test!".format(curMod[0]))
                    Mods.modStatus.update({curMod[0]: True})
                case (0 | 1):
                    curState = RobotState.testing
                    logging.debug("Testing student code...")
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.JOYBUTTONDOWN and event.button == controller.Button.B.value:
                    curState = RobotState.stopped
                    logging.warning("stop requested")
                    continue
            robot.keepAlive()
            robot.control.putBoolean("stop", False)
            hat.run(override="running")
            logging.debug("running student code")
            if not Mods.modStatus[curMod[0]]:  # makes sure module passed its last test
                logging.warning("Module {} has not passed its tests and cannot be run. Abort.".format(curMod[0]))
                curState = RobotState.stopped
                continue
            match Mods.run_module(curMod[0]):
                case 0:
                    continue
                case 1:
                    curState = RobotState.stopped
                    logging.error("Student code crashed!")
                    hat.run(override="dead")
                case 2:
                    curState = RobotState.stopped
                    logging.info("Student code exited gracefully")

        case RobotState.debug:
            # designed to update keepalive while students execute code in separate python console
            robot.keepAlive()
            robot.control.putBoolean("stop", False)
            hat.run(override="running")
            logging.debug("In debug mode")
            # Try to not let the robot drive
            robot.lDrive.Set(0)
            robot.rDrive.Set(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.KEYDOWN:
                    curState = RobotState.stopped
                    logging.warning("stop requested")
