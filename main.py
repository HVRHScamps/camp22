import logging
import string
from enum import Enum
import libhousy
import time
import pygame
from modhandler import modhandler
import display
pygame.init()
robot = libhousy.robot()
controller = libhousy.controller()
Mods = modhandler(["testme", "driveforward10", "autoPickup", "autoShoot", "gyroTurn", "holdStill"], robot)


class robotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3


curState = robotState.stopped
curMod: string


def teleop():
    lthr = controller.getAxis(controller.Axis.rStickY) + controller.getAxis(controller.Axis.rStickX)
    if abs(lthr) > 1:
        lthr = lthr/abs(lthr)
    rthr = controller.getAxis(controller.Axis.rStickY) - controller.getAxis(controller.Axis.rStickX)
    if abs(rthr) > 1:
        lthr = lthr / abs(lthr)
    robot.lDrive.Set(lthr)
    robot.rDrive.Set(rthr)
    time.sleep(0.01)


while True:
    if curState != robotState.stopped:
        robot.keepAlive()
        robot.control.putBoolean("stop", False)
    match curState:
        case robotState.stopped:
            logging.debug("robot stopped")
            robot.control.putBoolean("stop", True)
        case robotState.teleop:
            logging.debug("teleop mode")
            teleop()
        case robotState.testing:
            logging.info("testing student code...")
            match Mods.testModule(curMod):
                case 4:
                    curState = robotState.running
                case (0 | 1):
                    curState = robotState.testing
                case _:
                    curState = robotState.stopped
                    logging.error("Student code failed its tests!")
        case robotState.running:
            logging.debug("running student code")
            if not Mods.modStatus[curMod]:  # makes sure module passed its last test
                curState = robotState.testing
                continue
            if Mods.runModule(curMod) == 1:
                curState = robotState.stopped
                logging.error("Student code crashed!")
            for event in pygame.event.get():
                if event == pygame.JOYBUTTONDOWN:
                    curState = robotState.stopped
                    print("stop requested by xbox controller")
