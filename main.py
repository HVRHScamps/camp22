from email.policy import default
import libhousy
import logging
import string
from enum import Enum
from modhandler import modhandler
robot = libhousy.robot()
Mods = modhandler(["testme","driveforward10"])
class robotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3
curState = robotState.stopped
curMod: string
def teleop():
    #currently a stub function, need controller inputs from PyGame
    logging.error("no teleop code is defined!")

while True:
    if curState != robotState.stopped: 
        robot.keepAlive()
        robot.control.putBoolean("stop",False)
    match curState:
        case robotState.stopped:
            logging.debug("robot stopped")
            robot.control.putBoolean("stop",True)
        case robotState.teleop:
            logging.debug("teleop mode")
            teleop()
        case robotState.testing:
            logging.info("testing student code...")
            match Mods.testModule(curMod):
                case 4:
                    curState = robotState.running
                case (0|1):
                    curState = robotState.testing
                case _:
                    curState = robotState.stopped
                    logging.error("Student code failed its tests!")
        case robotState.running:
            logging.debug("running student code")