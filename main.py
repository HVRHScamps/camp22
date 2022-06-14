import logging
from enum import Enum
import libhousy
import time
import pygame
from modhandler import modhandler
import display
from teleop import Teleop

robot = libhousy.robot()
controller = libhousy.controller()
Mods = modhandler(["driveforward10", "autoPickup", "manualShoot", "autoShoot", "gyroTurn", "holdStill", "ph1", "ph2", "ph3", "ph4"], robot)
screen = display.Display()
to = Teleop(robot)


class RobotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3


curState = RobotState.stopped
curMod = [Mods.studentModules[0], 0]


def teleop():
    to.drive(controller.getAxis(controller.Axis.rStickX),controller.getAxis(controller.Axis.rStickY))
    robot.shootWheel.Set(int(controller.getButton(controller.Button.rBumper)))
    if controller.getAxis(controller.Axis.rTrigger) > 0.8:
        to.pickup()
    elif controller.getAxis(controller.Axis.lTrigger) > 0.8 and controller.getButton(controller.Button.rBumper):
        to.shoot()
    else:
        to.stop()
    to.anglehood(controller.getAxis(controller.Axis.rStickX))
    time.sleep(0.01)


def set_mod(num):
    global curMod
    curMod = [Mods.studentModules[num], num]
    screen.select_box(num)


while True:
    screen.run(Mods.studentModules, Mods.modStatus)
    if curState != RobotState.stopped:
        robot.keepAlive()
        robot.control.putBoolean("stop", False)
    match curState:
        case RobotState.stopped:
            logging.debug("robot stopped")
            robot.control.putBoolean("stop", True)
            for event in pygame.event.get():
                match event:
                    case pygame.CONTROLLER_BUTTON_DPAD_LEFT | pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                        if curMod[1] < 5:
                            newMod = curMod[1] + 5
                        else:
                            newMod = curMod[1] - 5
                        set_mod(newMod)
                    case pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                        newMod = curMod[1] + 1
                        if newMod > 9:
                            newMod = 0
                        set_mod(newMod)
                    case pygame.CONTROLLER_BUTTON_DPAD_UP:
                        newMod = curMod[1] - 1
                        if newMod < 0:
                            newMod = 9
                        set_mod(newMod)
                    case pygame.CONTROLLERBUTTONDOWN:
                        if controller.getButton(controller.Button.A):
                            curState = RobotState.testing
                            # TODO: switch sense hat mode
                        if controller.getButton(controller.Button.hamburger):
                            curState = RobotState.teleop

        case RobotState.teleop:
            logging.debug("teleop mode")
            teleop()
            if controller.getButton(controller.Button.hamburger):
                curState = RobotState.stopped
        case RobotState.testing:
            logging.info("testing student code...")
            match Mods.testModule(curMod[0]):
                case 4:
                    curState = RobotState.running
                case (0 | 1):
                    curState = RobotState.testing
                case _:
                    curState = RobotState.stopped
                    logging.error("Student code failed its tests!")
                    if controller.getButton(controller.Button.A):
                        curstate = RobotState.teleop
        case RobotState.running:
            logging.debug("running student code")
            if not Mods.modStatus[curMod[0]]:  # makes sure module passed its last test
                curState = RobotState.testing
                continue
            match Mods.runModule(curMod[0]):
                case 0:
                    break
                case 1:
                    curState = RobotState.stopped
                    logging.error("Student code crashed!")
                    Mods.modStatus.update(curMod[0], False)  # make note of failure
                case 2:
                    curState = RobotState.stopped
                    logging.info("Student code exited gracefully")
            for event in pygame.event.get():
                if event == pygame.CONTROLLERBUTTONDOWN:
                    curState = RobotState.stopped
                    print("stop requested by xbox controller")
