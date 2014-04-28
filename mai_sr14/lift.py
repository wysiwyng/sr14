import time, threading
from sr import *

class Lift(threading.Thread):
    def __init__(self, robot, debug = None):
        threading.Thread.__init__(self)
        self.debug = debug
        self.debugMsg("constructing lift thread")
        self.motor = robot.motors[0].m0
        self.rduino = robot.ruggeduinos[0]
        self.rduino.pin_mode(10, INPUT_PULLUP)
        self.newCommand = threading.Event()
        self.actionFinished = threading.Event()
        self.actionFinished.set()
        if self.getState() == 4:
            self.command = 0
            self.newCommand.set()
            self.actionFinished.clear()
        self.debugMsg("lift thread ready")
        
    def run(self):
        self.debugMsg("running lift thread")
        
        while(True):
            self.debugMsg("waiting for new commands")
            self.newCommand.wait()
            self.actionFinished.clear()
            self.rduino.warn_on()
            self.debugMsg("new commands available, evaluating command variable")
            state = self.getState()
            
            if self.command != state:
                if self.command < state:
                    self.motor.power = -100
                
                if self.command > state:
                    self.motor.power = 100
                
                self.waitForState(self.command)
                self.motor.power = 0
            
            self.debugMsg("command executed, setting actionFinished flag and resetting command")
            self.command = -1
            self.newCommand.clear()
            self.actionFinished.set()
            self.rduino.warn_off()

    def grabToken(self, height = 1):
        self.rduino.warn_on()
        self.debugMsg("grabbing token, activating pump and moving downwards")
        self.rduino.digital_write(8, True) #pumpe an
        self.motor.power = -80
        self.debugMsg("waiting for pressure to fall")
        
        while self.rduino.digital_read(10) == True:
            if self.getState() == 0:
                self.debugMsg("reached bottom position and no token, aborting")
                self.releaseToken()
                self.motor.power = 0
                self.tokenHeightAsync()
                return False
                
        self.debugMsg("moving arm to token height")
        self.motor.power = 100
        self.waitForState(height)
        self.motor.power = 0
        self.debugMsg("arrived at token height, returning")
        self.rduino.warn_off()
        return True
        
    def prepareTurnToken(self):
        self.rduino.warn_on()
        self.debugMsg("activating pump")
        self.rduino.digital_write(8, True)
        self.debugMsg("pump should be running")
        self.debugMsg("lower arm")
        self.motor.power = -80
        
        while self.rduino.digital_read(10) == True:
            if self.getState() == 0:
                self.debugMsg("reached bottom position and no token, aborting")
                self.releaseToken()
                self.motor.power = 0
                self.tokenHeightAsync()
                return False
        self.debugMsg("token found - stop lowering arm")        
        self.motor.power = 0
        self.debugMsg("deactivate pump")
        self.rduino.digital_write(8, False)
        self.rduino.warn_off()

    def releaseToken(self):
        self.debugMsg("releasing token")
        self.rduino.digital_write(8, False)
        self.debugMsg("waiting for pressure to rise")
        while self.hasToken():
            pass
        self.debugMsg("token released")

    def hasToken(self):
        if self.rduino.digital_read(10) == False:
            self.debugMsg("token is present")
            return True
        else:
            self.debugMsg("no token present")
            return False
    
    def bottom(self):
        self.bottomAsync()
        self.debugMsg("waiting for command to finish")
        self.actionFinished.wait()
    
    def tokenHeight(self):
        self.tokenHeightAsync()
        self.debugMsg("waiting for command to finish")
        self.actionFinished.wait()
        
    def driveHeight(self):
        self.driveHeightAsync()
        self.debugMsg("waiting for command to finish")
        self.actionFinished.wait()
        
    def top(self):
        self.topAsync()
        self.debugMsg("waiting for command to finish")
        self.actionFinished.wait()

    def bottomAsync(self):
        self.debugMsg("signalling main thread to move to bottom position")
        self.command = 0
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
    
    def tokenHeightAsync(self):
        self.debugMsg("signalling main thread to move to token height")
        self.command = 1
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def driveHeightAsync(self):
        self.debugMsg("signalling main thread to mave to driving height")
        self.command = 2
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def topAsync(self):
        self.debugMsg("signalling main thread to move to top position")
        self.command = 3
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def getState(self):
        with self.rduino.lock:
            temp = int(self.rduino.command('a' + self.rduino._encode_pin(10)))
        
        if temp < 5 and temp > -1:
            #self.debugMsg("setting lift height to {0}".format(temp))
            return temp
            
        else:
            self.debugMsg("something is wrong with the lift, setting state to -1, state is {0}".format(temp))
            return -1

    def debugMsg(self, text):
        if self.debug != None:
            self.debug.printMsg(text, self)
    
    def afterTokenTurn(self):
        self.motor.power = 100
        self.waitForState(1)
        self.motor.power = 0
    
    def waitForState(self, state):
        self.debugMsg("waiting for state to become {0}".format(state))
        while self.getState() != 4:
            pass
        self.debugMsg("in movement now waiting")
        temp = self.getState()
        while True:
            self.debugMsg("state is {0}".format(temp))
            if temp == state:
                self.debugMsg("reached state {0}".format(state))
                return True
            elif temp == 0 or temp == 3:
                self.debugMsg("something went wrong, we're at state {0}".format(temp))
                return False
            temp = self.getState()
        
    def __str__(self):
        return "lift"
        
