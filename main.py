import logging
from enum import Enum
import libhousy
import time
import pygame
from modhandler import modhandler
import display

robot = libhousy.robot()
controller = libhousy.controller()
Mods = modhandler(["driveforward10", "autoPickup", "manualShoot", "autoShoot", "gyroTurn", "holdStill"], robot)
screen = display.Display()


class RobotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3


curState = RobotState.stopped
curMod = [Mods.studentModules[0], 0]
to_shoot_toggle = False


def teleop():
    global to_shoot_toggle
    lthr = controller.getAxis(controller.Axis.rStickY) + controller.getAxis(controller.Axis.rStickX)
    if abs(lthr) > 1:
        lthr = lthr / abs(lthr)
    rthr = controller.getAxis(controller.Axis.rStickY) - controller.getAxis(controller.Axis.rStickX)
    if abs(rthr) > 1:
        rthr = rthr / abs(rthr)
    robot.lDrive.Set(lthr)
    robot.rDrive.Set(rthr)
    robot.shootWheel.Set(int(to_shoot_toggle))
    if controller.getButton(controller.Button.rBumper):
        to_shoot_toggle = not to_shoot_toggle
    if controller.getAxis(controller.Axis.rTrigger) > 0.8:
        robot.pickupMotor.Set(1)
        robot.pickupPneumatic.Extend()
        robot.beltZ1.Set(-0.8)
        robot.beltZ2.Set(0)
        robot.beltZ3.Set(0)
        robot.upperTension.Retract()
        robot.lowerTension.Extend()
    elif controller.getAxis(controller.Axis.lTrigger) > 0.8 and to_shoot_toggle:
        robot.beltZ1.Set(-0.8)
        robot.beltZ2.Set(-0.8)
        robot.beltZ3.Set(1)
        robot.upperTension.Extend()
        robot.lowerTension.Retract()
    else:
        robot.pickupMotor.Set(0)
        robot.pickupPneumatic.Retract()
        robot.beltZ1.Set(0)
        robot.beltZ2.Set(0)
        robot.beltZ3.Set(0)
    if controller.getAxis(controller.Axis.rStickX) > 0.4:
        robot.shootAngle.Extend()
    elif controller.getAxis(controller.Axis.rStickX) < -0.4:
        robot.shootAngle.Retract()
    else:
        robot.shootAngle.Stop()

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
