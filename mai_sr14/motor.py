#    Copyright (C) 2105  wysiwyng
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time, threading, pyudev, serial
    
class MotorBlockException(Exception):
    def __init__(self, x):
        self.opcode = x
    
    def __str__(self):
        return "Motor is blocked"

class Motor(threading.Thread):
    def __init__(self, boardId, debug = None):
        threading.Thread.__init__(self)
        self.debug = debug
        self.debugMsg("constructing motor thread")
        self.boardId = boardId
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.command = 0
        self.speed = 0
        self.direction = 0
        self.distance = 0
        self.motor = 0
        self.inited = False
        self.newCommand = threading.Event()
        self.actionFinished = threading.Event()
        self.actionFinished.set()
        self.debugMsg("motor thread ready")
    
    def _findDev(self):
        "Find the serial port associated with the USB-ISS module"
        c = pyudev.Context()
    
        for tty in c.list_devices( subsystem="tty" ):
            p = tty.find_parent( subsystem="usb", device_type = "usb_device" )
            if p is None:
                continue
    
            if p["ID_SERIAL"] == self.boardId:
                return tty.device_node
        
        return None
    
    def run(self):
        self.debugMsg("running motor thread")
        if not self.inited:
            print "motor board not initialized, cannot start motor thread"
            return
        
        while(True):
            self.debugMsg("waiting for new commands")
            self.newCommand.wait()
            self.actionFinished.clear()
            self.debugMsg("new commands available, evaluating command variable")
            
            if self.command == 1: # drive forward
                self.debugMsg("command is 1, drive forwards")
                self.sendSerialCommand(220)
                
            elif self.command == 2: # drive backward
                self.debugMsg("command is 2, drive backwards")
                self.sendSerialCommand(216)
                
            elif self.command == 3: # active brake
                self.debugMsg("command is 3, active brake")
                if self.motor == 1:
                    self.sendSerialCommand(221)
                elif self.motor == 2:
                    self.sendSerialCommand(219)
                else:
                    self.sendSerialCommand(217)
                
            elif self.command == 4: # passive brake
                self.debugMsg("command is 3, active brake")
                if self.motor == 1:
                    self.sendSerialCommand(220)
                elif self.motor == 2:
                    self.sendSerialCommand(218)
                else:
                    self.sendSerialCommand(216)
                
            elif self.command == 5: # turn left
                self.debugMsg("command is 5, turn left")
                self.sendSerialCommand(218)
                
            elif self.command == 6: # turn right
                self.debugMsg("command is 6, turn right")
                self.sendSerialCommand(222)
            
            self.debugMsg("command executed, resetting newCommand flag and setting actionFinished flag")
            self.speed = 0
            self.direction = 0
            self.distance = 0
            self.motor = 0
            self.newCommand.clear()
            self.actionFinished.set()
    
    def init(self, _reset = False):
        self.debugMsg("finding motor board")
        port = self._findDev()
        if port == None:
            self.debugMsg("board not found!!!!!!!!!1111")
            raise IOError("no motor board connected")
            
        self.debugMsg("port is " + port)
        self.debugMsg("opening port")
        self.ser.port = port
        self.ser.open()
        #self.debugMsg("reading version from controller")
        #self.ser.write('v')
        #res = self.ser.read(1)
        #self.debugMsg("got response, controller version is {0}".format(str(ord(res))))
        self.inited = True
        time.sleep(0.1)
        self.debugMsg("motor board initialized and ready for action")
        self.activeBrake()
        
    def reset(self):
        self.debugMsg("opening com port at 1200 baud")
        self.ser.close()
        self.ser.baudrate = 1200
        self.ser.open()
        self.ser.close()
        self.ser.baudrate = 115200
        time.sleep(10)
        self.ser.open()
        
    def sendSerialCommand(self, _instruction):
        self.debugMsg("sending serial command: $ {0} {1} {2} {3} {4}".format(_instruction, self.speed, self.direction, (self.distance >> 8) & 0xff, self.distance % 0xff))
        self.ser.write('$')
        self.ser.write(chr(_instruction))
        self.ser.write(chr(self.speed))
        self.ser.write(chr(self.direction))
        self.ser.write(chr((self.distance >> 8) & 0xff))
        self.ser.write(chr(self.distance % 0xff))
        self.debugMsg("serial command sent, awaiting response")
        self.ser.read(1)
        instruction = ord(self.ser.read(1))
        self.ser.read(4)
        self.debugMsg("response received")
        self.actionFinished.set()
        if instruction != _instruction:
            self.debugMsg(instruction)
            self.debugMsg(_instruction)
            self.debugMsg("different instruction, error occurred")
            raise MotorBlockException(instruction)
        return True
        
    def driveForwardAsync(self, _speed, _direction = 0, _distance = 0):
        self.debugMsg("signalling main thread to drive forwards")
        self.speed = int(_speed)
        self.direction = int(_direction)
        self.distance = int(_distance)
        self.command = 1
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def driveBackwardAsync(self, _speed, _direction = 0, _distance = 0):
        self.debugMsg("signalling main thread to drive backwards")
        self.speed = int(_speed)
        self.direction = int(_direction)
        self.distance = int(_distance)
        self.command = 2
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def activeBrakeAsync(self, _motor = 0):
        self.debugMsg("signalling main thread to brake actively")
        self.motor = _motor
        self.command = 3
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def passiveBrakeAsync(self, _motor = 0):
        self.debugMsg("signalling main thread to passively brake")
        self.motor = _motor
        self.command = 4
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def turnLeftAsync(self, _speed, _degrees = 0):
        self.debugMsg("signalling main thread to turn left")
        self.speed = _speed
        self.distance = _degrees
        self.command = 5
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def turnRightAsync(self, _speed, _degrees = 0):
        self.debugMsg("signalling main thread to turn right")
        self.speed = int(_speed)
        self.distance = int(_degrees)
        self.command = 6
        self.newCommand.set()
        self.debugMsg("signal sent, should be processed immediatly")
        
    def driveForward(self, _speed, _direction = 0, _distance = 0):
        self.speed = _speed
        self.direction = _direction
        self.distance = int(_distance)
        return self.sendSerialCommand(220)
        #self.driveForwardAsync(_speed, _direction, _distance)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
        
    def driveBackward(self, _speed, _direction = 0, _distance = 0):
        self.speed = _speed
        self.direction = _direction
        self.distance = int(_distance)
        return self.sendSerialCommand(216)
        #self.driveBackwardAsync(_speed, _direction, _distance)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
    
    def activeBrake(self, _motor = 0):
        if _motor == 1:
            return self.sendSerialCommand(221)
        elif _motor == 2:
            return self.sendSerialCommand(219)
        else:
            return self.sendSerialCommand(217)
        #self.activeBrakeAsync(_motor)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
    
    def passiveBrake(self, _motor = 0):
        self.speed = 0
        if _motor == 1:
            return self.sendSerialCommand(220)
        elif _motor == 2:
            return self.sendSerialCommand(218)
        else:
            return self.sendSerialCommand(216)
        #self.passiveBrakeAsync(_motor)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
        
    def turnLeft(self, _speed, _degrees = 0):
        if _degrees < 3:
            _degrees = 3
        self.speed = _speed
        self.distance = int(_degrees)
        return self.sendSerialCommand(218)
        #self.turnLeftAsync(_speed, _degrees)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
    
    def turnRight(self, _speed, _degrees = 0):
        self.speed = _speed
        self.distance = int(_degrees)
        return self.sendSerialCommand(222)
        #self.turnRightAsync(_speed, _degrees)
        #self.debugMsg("waiting for command to finish")
        #self.actionFinished.wait()
        
    def debugMsg(self, message):
        if self.debug != None:
            self.debug(message, self)
    
    def __str__(self):
        return "motor"
