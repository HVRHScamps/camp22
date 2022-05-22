'''A Fake robot class so that we can test student code in a controlled enviornment'''

import string
class motor:
    '''abstraction for FRC motor controller / motor controller group'''
    def __init__(self,name: string):
        self.name = name
        self.value = 0
    def Set(self,value: int):
        '''Sets motor speed in a range from -1 to 1
        where -1 is full reverse, 1 is full forward, and 0 is stopped'''
        if abs(value) > 1: raise ValueError("Out of range input supplied!!")
        else: self.value = value

class servo:
    def __init__(self,name: string):
        self.name = name
        self.value = 0
    def Set(self,value: int):
        '''sets the servo to a specified angle in degrees. Valid inputs are 0-180.'''
        if value > 180 or value < 0: raise ValueError("Out of range input supplied!!")
        else: self.value = value
class pneumatic:
    '''abstraction for FRC Double Solenoid class'''
    def __init__(self, name: string):
        self.name = name
        self.value = 0
    def Extend(self):
        '''sets pneumatic to kForward'''
        self.value = 1
    def Retract(self):
        '''sets pneumatic to kReverse'''
        self.value = -1
    def Stop(self):
        '''sets pneumatic to kOff'''
        self.value = 0

class encoder:
    '''abstraction for FRC Encoder (and geartooth) class'''
    def __init__(self,name: string,index: int):
        self.value = 0
    def Get(self):
        '''returns the number of encoder cycles since last reset'''
        return self.value
    def Reset(self):
        '''sets encoder value to 0'''
        self.value = 0

class colorSensor:
    '''Abstraction for REV color sensor V3'''
    def __init__(self):
        self.value = [0,0,0]
        self.prox = 0
    def getColor(self):
        """returns an array of RGB color values from 0-255"""
        return self.value
    def getProximity(self):
        '''returns *raw* proximity value ranging from 0 to 2047 with 2047 being 
        closest to the sensor and 0 being furthest away / not detected'''
        return self.prox

class robot:
    def __init__(self):
        # motors
        self.lDrive = motor("driveL")
        self.rDrive = motor("driveR")
        self.beltZ1 = motor("beltZ1")
        self.beltZ2 = motor("beltZ2")
        self.beltZ3 = motor("beltZ3")
        self.shootWheel = motor("shootWhl")
        self.shootAngle = pneumatic("shootPos") 
        '''a relay, not a pneumatic but they behave the same way. call Extend or Retract until it's at a good angle then call Stop'''
        self.pickupMotor = motor("pickupM")
        self.colorPanelMotor = motor("clrPnlM")
        self.climber = motor("climber")
        self.climbServo = servo("climberServo")
        # sensors
        self.shootEncoder = encoder("shootEncoder",1)
        self.lDriveEncoder = encoder("driveEncoderL",2)
        self.rDriveEncoder = encoder("driveEncoderR",3)
        self.shootCounter = encoder("shootCounter",4) #not technically an encoder
        self.colorSensor = colorSensor()
        # Pneumatics
        self.colorPanelPneumatic = pneumatic("clrPnlPNM")
        self.pickupPneumatic = pneumatic("pickupPNM")
        self.lowerTension = pneumatic("lTensPNM")
        self.upperTension = pneumatic("uTensPNM")
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
    def getYaw(self):
        '''returns the yaw (side-to-side pivot) of the robot in degrees''' 
        return self.yaw
    def getRoll(self):
        '''returns the roll (side-to-side tilt) of the robot in degrees''' 
        return self.roll
    def getPitch(self):
        '''returns the pitch (front-back tilt) of the robot in degrees''' 
        return self.pitch
    def getAcceleration(self,axis: string):
        '''returns the acceleration in Gs for the specified axis. Valid inputs: "x", "y", "z".
        Note that the qoutation marks are required!'''
        return 0 #I'm not gonna bother simulating acceleration LMAO