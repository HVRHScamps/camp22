import logging
import string
from enum import Enum
import libhousy
import time
import pygame
from modhandler import modhandler
import display

robot = libhousy.robot()
controller = libhousy.controller()
Mods = modhandler(["testme", "driveforward10", "autoPickup", "autoShoot", "gyroTurn", "holdStill"], robot)


class RobotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3


curState = RobotState.stopped
curMod: string


def teleop():
    lthr = controller.getAxis(controller.Axis.rStickY) + controller.getAxis(controller.Axis.rStickX)
    if abs(lthr) > 1:
        lthr = lthr / abs(lthr)
    rthr = controller.getAxis(controller.Axis.rStickY) - controller.getAxis(controller.Axis.rStickX)
    if abs(rthr) > 1:
        lthr = lthr / abs(lthr)
    robot.lDrive.Set(lthr)
    robot.rDrive.Set(rthr)
    time.sleep(0.01)


while True:
    if curState != RobotState.stopped:
        robot.keepAlive()
        robot.control.putBoolean("stop", False)
    match curState:
        case RobotState.stopped:
            logging.debug("robot stopped")
            robot.control.putBoolean("stop", True)
        case RobotState.teleop:
            logging.debug("teleop mode")
            teleop()
        case RobotState.testing:
            logging.info("testing student code...")
            match Mods.testModule(curMod):
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
            if not Mods.modStatus[curMod]:  # makes sure module passed its last test
                curState = RobotState.testing
                continue
            if Mods.runModule(curMod) == 1:
                curState = RobotState.stopped
                logging.error("Student code crashed!")
            for event in pygame.event.get():
                if event == pygame.JOYBUTTONDOWN:
                    curState = RobotState.stopped
                    print("stop requested by xbox controller")
