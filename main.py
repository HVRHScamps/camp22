import enum
import libhousy
import logging
from enum import Enum
robot = libhousy.robot()

class robotState(Enum):
    stopped = 0
    teleop = 1
    testing = 2
    running = 3
curState = robotState.stopped

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
        case robotState.running:
            logging.debug("running student code")