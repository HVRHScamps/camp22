import importlib
import libhousy
import string
import time
import logging
class modhandler:
    def __init__(self, studentMods:list, robot:libhousy.robot):
        '''initializes student module subsystem, takes a lits of all modules as an argument'''
        self.falseAutomaton = libhousy.robot(True)
        self.robot = robot
        self.studentModules = studentMods
        self.testStatus = 0
        '''0- not running, 1- running, 2-failed requirements, 3-runtime error 4-pass'''
        self.testStartTime = 0
        self.testStage = 0
        '''Flag to indicate wheather testing is in progress'''
        mods = {}
        for mod in self.studentModules:
            mods.update({mod:importlib.import_module(mod)})

    def testModule(self,modulename: string):
        if self.testStatus == 0:
            self.testStartTime = time.time()
            self.runningTests = 1
        subject = self.mods[modulename]
        importlib.reload(subject)
        match modulename:
                case "driveforward10":
                    match self.testStage:
                        case 0:
                            if (self.falseAutomaton.lDrive.value > 0 and self.falseAutomaton.rDrive.value > 0):
                                self.testStage +=1
                            elif (time.time() - self.testStartTime > 2):
                                logging.error("Did not try to drive forward after 2s. fail.")
                                self.testStatus = 2
                        case 1:
                            self.falseAutomaton.lDriveEncoder.value = self.falseAutomaton.lDrive.value*10 #temporary estimation
                            self.falseAutomaton.rDriveEncoder.value = self.falseAutomaton.rDrive.value*10 #temporary estimation
                            if abs(self.falseAutomaton.lDriveEncoder.value-self.falseAutomaton.rDriveEncoder.value) > 30:
                                logging.error("turned when it shouldn't")
                                self.teststatus = 2
                            if abs(50000 - self.falseAutomaton.lDriveEncoder.Get()) < 50:
                                self.testStage +=1
                            elif (self.falseAutomaton.lDriveEncoder.Get()>50050): #TODO: replace with actual value
                                #safe to only use left drive encoder here since above we ensure they are roughly equal
                                logging.error("overshot target")
                                self.testStatus = 2
                            elif time.time()-self.testStartTime>10:
                                logging.error("took too long!")
                                self.teststatus = 2
                        case _:
                            #since we're out of bounds, assume success due to pass case addition
                            self.testStatus = 4
                            logging.info("passed all tests")
                case _:
                    logging.warning("No testing profile defined for module")
                    logging.warning("running stability-only test")
        try:          
            subject.main(self.falseAutomaton)
        except:
            return 3
        return self.testStatus
    
    def runModule(self,modulename: string):
        ''''Returns: 0 - done, 1 - running, 2 - internal fault'''
        subject = self.mods[modulename]
        importlib.reload(subject)
        try:
            subject.main(self.robot)
        except:
            return 1
        return 0
