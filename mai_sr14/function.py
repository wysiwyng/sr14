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

import time, math
from sr import *
markerTypes = ["Arena Marker", "Robot Marker", "Slot Marker", "Token Marker Top", "Token Marker Bottom", "Token Marker Side"]


class Driver(object):
    def __init__(self, robot, motor, maxSpeed = 255, maxTurnSpeed = 150, distModifier = 10, distModifierBegin = 80, camRes = (800, 600), debug = None):
        self.debug = debug
        self.debugMsg("constructing driver object which is totally not the drivingFunctions object from the last story")
        self.robot = robot
        self.motor = motor
        self.maxSpeed = maxSpeed
        self.maxTurnSpeed = maxTurnSpeed
        self.distModifier = distModifier
        self.distModifierBegin = distModifierBegin
        self.camRes = camRes

    def getMarkerAtOffset(self, markers, type, offset = -1):
        markers.sort(key = lambda x: x.dist)
        for m in markers:
            if m.info.offset == offset and m.info.marker_type == type:
                self.debugMsg("found {0} {1}, returning it".format(markerTypes[type], offset))
                return m
            elif offset == -1 and m.info.marker_type == type:
                self.debugMsg("found a {0}, returning the nearest".format(markerTypes[type]))
                return m

    def getTokenMarker(self, markers, offset):
        markers.sort(key = lambda x: x.dist)
        types = [MARKER_TOKEN_TOP, MARKER_TOKEN_SIDE, MARKER_TOKEN_BOTTOM]
        sameMarkers = []
        for m in markers:
            for t in types:
                if m.info.offset == offset and m.info.marker_type == t:
                    self.debugMsg("found a {0} with offset {1}".format(markerTypes[t], offset))
                    sameMarkers.append(m)
        if len(sameMarkers) == 0:
            self.debugMsg("found no marker; returning")
            return None
        if len(sameMarkers) == 1:
            return sameMarkers[0]
            self.debugMsg("found one marker; returning")
        
        tempMarker = sameMarkers[0]
        self.debugMsg(" found more than one of the same marker; compairing")
        for m in sameMarkers:
            if abs(m.orientation.rot_y) < abs(tempMarker.orientation.rot_y):
                tempMarker = m
        return tempMarker
    
    def lookForSlot(self, offset):
        self.debugMsg("searching slot {0}".format(offset))
        time.sleep(0.3)
        self.debugMsg("looking for slot")
        markers = self.robot.see(self.camRes)        
        self.debugMsg("found {0} markers".format(len(markers)))
        tempMarker = self.getMarkerAtOffset(markers, MARKER_ARENA, offset)
        if tempMarker != None:
            self.debugMsg("found no slot {0}, returning--------------------------".format(offset))
            return tempMarker
            
    def lookForToken(self, offset, direction = True, degrees = 20):
        self.debugMsg("searching token {0}".format(offset))
        time.sleep(0.3)
        self.debugMsg("looking for markers")
        markers = self.robot.see(self.camRes)        
        self.debugMsg("found {0} markers".format(len(markers)))
        tempMarker = self.getTokenMarker(markers, offset)
        if tempMarker != None:
            self.debugMsg("found token {0}, returning".format(offset))
            return tempMarker
        self.search(degrees, direction)
        return None

    def lookForMarkers(self, type, offset = -1, direction = True, degrees = 20):
        self.debugMsg("searching marker {0}".format(offset))
        self.debugMsg("stabilizing camera")
        time.sleep(0.3)
        self.debugMsg("looking for markers")
        markers = self.robot.see(self.camRes)
        self.debugMsg("found {0} markers".format(len(markers)))
        tempMarker = self.getMarkerAtOffset(markers, type, offset)
        if tempMarker != None:
            self.debugMsg("found the marker, returning")
            return tempMarker
        self.search(degrees, direction)
        return None
    
    def search(self, degrees, direction):
        self.debugMsg("no marker found, turning {0} degrees".format(degrees))
        if direction:
            self.motor.turnRight(self.maxTurnSpeed + 40, degrees)
        else:
            self.motor.turnLeft(self.maxTurnSpeed + 40, degrees)    

    def turnToMarker(self, marker, tolerance = 4): #a function to determine if the robot is centerd within 5 degrees of the given marker and if not to correct the deviation
        if abs(marker.rot_y) > tolerance:
            self.debugMsg("centering on marker")
            angle = int(abs(marker.rot_y))
            if marker.rot_y > 0:
                self.debugMsg("correcting {0} deg to the right".format(angle))
                self.motor.turnRight(self.maxTurnSpeed - 30, angle)
            else:
                self.debugMsg("correcting {0} deg to the left".format(angle))
                self.motor.turnLeft(self.maxTurnSpeed - 30, angle)
            self.debugMsg("should now be centered, look again to verify")
            return False
        
        self.debugMsg("marker is within +- 5 degrees, continuing")
        return True
        
    def driveToCenterAxisMk2(self, marker, distance): #a function which leads us diagonal 45 cm before the wanted marker
        self.debugMsg("attempting to get to markers center axis")
        _distToM = marker.dist * 100 #distance to marker
        _direction = marker.orientation.rot_y > 0
        _distToD = _distToM**2 + distance**2 - (2 * _distToM * distance * math.cos(math.radians(abs(marker.orientation.rot_y)))) #distance to drive square
        _distToD = math.sqrt(_distToD) #getting rid of the square
        _beta = math.degrees(math.acos((_distToM**2 + _distToD**2 - distance**2) / (2 * _distToM * _distToD))) #angle to turn
        _alpha = 180 - _beta - abs(marker.orientation.rot_y)
        _gAlpha = 180 - _alpha

        if _distToD > self.distModifierBegin:
            _distToD -= self.distModifier

        if _distToD < 10 or _beta < 2 or _gAlpha < 2 or _distToM < distance:
            self.debugMsg("exiting: distToD: {0}, beta: {1}, gAlpha: {2}, distToM: {3}, distance: {4}".format(_distToD, _beta, _gAlpha, _distToM, distance))
            return True
            
        if _direction:
            self.debugMsg("now turning {0} degrees to the left".format(_beta))
            self.motor.turnLeft(self.maxTurnSpeed - 20, int(_beta))
            time.sleep(0.3)
            
            self.debugMsg("driving {0} cm forward".format(_distToD))
            self.motor.driveForward(int(self.maxSpeed - 50), 0, int(_distToD))
            time.sleep(0.3)
            
            self.debugMsg("turning {0} degrees to the right".format(_gAlpha))
            self.motor.turnRight(self.maxTurnSpeed - 20, int(_gAlpha))
        else:
            self.debugMsg("now turning {0} degrees to the right".format(_beta))
            self.motor.turnRight(self.maxTurnSpeed - 20, int(_beta))
            time.sleep(0.3)
            
            self.debugMsg("driving {0} cm forward".format(_distToD))
            self.motor.driveForward(int(self.maxSpeed - 50), 0, int(_distToD))
            time.sleep(0.3)
            
            self.debugMsg("turning {0} degrees to the left".format(_gAlpha))
            self.motor.turnLeft(self.maxTurnSpeed - 20, int(_gAlpha))
        
        return False

    def driveToCenterAxis(self, marker): #a function to test if the robot is out of the center axis of the given marker and if yes to drive to it
        _distance = marker.dist * 100 #some variables & calculations to determine & store the distances and angles needed
        _mRotY = abs(marker.orientation.rot_y)
        _mCRotY = abs(marker.rot_y)
        _angleToTurn = 90 - _mRotY
        _distToDrive = math.sin(math.radians(_mRotY)) * _distance
        _direction = marker.orientation.rot_y > 0
    
        if _mRotY < 5 or _distToDrive < 10:
            self.debugMsg("already centered or too near to center axis, returning")
            return True
    
        self.debugMsg("attempting to get on markers center axis:")
        self.debugMsg("turn angle is {0} degrees".format(_angleToTurn))
        self.debugMsg("drive distance is {0} cm".format(_distToDrive))
    
        if _direction:
            self.debugMsg("we are standing right of the marker, turning left")
            self.motor.turnLeft(self.maxTurnSpeed -20, int(_angleToTurn))
        else:
            self.debugMsg("we are standing left of the marker, turning right")
            self.motor.turnRight(self.maxTurnSpeed -20, int(_angleToTurn))
    
        time.sleep(0.2)
    
        self.debugMsg("driving towards center axis")
        self.motor.driveForward(int(self.maxSpeed - 60), 0, int(_distToDrive))
    
        time.sleep(0.2)
    
        if _direction:
            self.debugMsg("started right of the marker, now turning back right")
            self.motor.turnRight(self.maxTurnSpeed, 90)
        else:
            self.debugMsg("started left of the marker, now turning back left")
            self.motor.turnLeft(self.maxTurnSpeed, 90)
    
        self.debugMsg("should now be on markers center axis, look again to verify")
        return False
       
    def driveTowardsMarker(self, marker, distance): #a function to determine if the robot is within a given distance in cm to a given marker and if not to drive towards it
        if marker.dist * 100 - distance > 10:
            self.debugMsg("driving {0} cm towards the marker".format(marker.dist * 100 - distance))
            self.motor.driveForward(int(self.maxSpeed - 70), 0, int(marker.dist * 100 - distance))
            return False
        else:
            self.debugMsg("too near to the marker, returning")
            return True

    def lookForTokenAbove(self, wantedMarker, markers):
        for m in markers:
            if abs(m.centre.world.y - wantedMarker.centre.world.y) > 0.25 and abs(m.centre.world.y - wantedMarker.centre.world.y) < 0.35 and (abs(m.rot_y) - abs(wantedMarker.rot_y)) > -1.5 and (abs(m.rot_y) - abs(wantedMarker.rot_y)) < 1.5:
                return True
        return False
    
    def driveOnMarker(self, type, offset = -1, direction = False, dist = 200, camRes = (1280, 960)):
        self.debugMsg("now driving with driveOnMarker to arenamarker {0}".format(offset))
        state = 0
        degrees = 20
        self.camRes = camRes
        while state != -1:
            if state == 0:
                wantedMarker = self.lookForMarkers(type, offset, direction, degrees)
                if wantedMarker == None:
                    self.debugMsg("wanted marker was not found, setting state to 0")
                    state = 0
                else:
                    self.debugMsg("found expected marker; setting state to 1")
                    state = 1
            
            elif state == 1:
                self.debugMsg("state is 1, turn to marker")
                if self.turnToMarker(wantedMarker):
                    self.debugMsg("facing marker directly; setting state to 2")
                    state = 2
                else:
                    self.debugMsg("not facing; correcting orientation; state is 0")
                    state = 0
            
            elif state == 2:
                if self.driveTowardsMarker(wantedMarker, dist):
                    self.debugMsg("we are now in our wanted position; exiting main loop; state is -1")
                    state = -1
                else:
                    self.debugMsg("our distance to our marker is too damn high; driving forward; state is 0")
                    state = 0
        
        return wantedMarker

    def driveToSlot(self, offset, direction = False):
        self.debugMsg("searching slot {0}".format(offset))
        state = 0
        counter = 0
        maxTries = 4
        while state != -1:
            if state == 0:
                if counter > maxTries:
                    self.debugMsg("counter is {0}".format(counter))
                    self.debugMsg("didnt find slot, maybe its blocked, returning")
                    raise SyntaxError, "the syntaxerror is a lie"
                    
                self.debugMsg("state 0, searching marker")
                wantedMarker = self.lookForMarkers(MARKER_SLOT, offset, direction, 15)
                
                if wantedMarker == None:
                    self.debugMsg("didnt see any markers, continuing search")
                    counter += 1
                    state = 0
                else:
                    counter = 0
                    self.debugMsg("found slot, setting state to 1")
                    state = 1
            
            elif state == 1:
                self.debugMsg("state is 1, turn to marker")
                if self.turnToMarker(wantedMarker):
                    self.debugMsg("facing marker directly; setting state to 2")
                    state = 2
                else:
                    self.debugMsg("not facing; correcting orientation; state is 0")
                    state = 0      
                    
            elif state == 2:
                self.debugMsg("state is 2, drive to markers center axis using mk2 routine")
                res = False
                if maxTries > 0:
                    self.debugMsg("we have {0} tries left, attempting mk2 routine".format(maxTries))
                    res = self.driveToCenterAxisMk2(wantedMarker, 60)
                    maxTries -= 1
                    if res:
                        self.debugMsg("no correction necessary, setting state to 3")
                        state = 3
                    else:
                        self.debugMsg("corrected, looking again, setting state to 0")
                        state = 0
                else:
                    self.debugMsg("no tries left, setting state to 3")
                    state = 3
                    
            elif state == 3:
                self.debugMsg("state is 3, drive to markers center axis, using mk1 routine")
                if self.driveToCenterAxis(wantedMarker):
                    self.debugMsg("perfectly on center axis, setting state to 4")
                    state = 4
                else:
                    self.debugMsg("not on center axis, corrected, setting state to 0")
                    state = 0
                    
            elif state == 4:
                if self.driveTowardsMarker(wantedMarker, 40):
                    self.debugMsg("we are now in our wanted position; exiting main loop; state is -1")
                    state = -1
                else:
                    self.debugMsg("our distance to our marker was too damn high; drove forward; state is 0")
                    state = 0
        return wantedMarker
            
    def driveToMarker(self, type, distMk2, dist, offset = -1, pendulum = False,  direction = False, maxTries = 2, useMk1 = False, camRes = (800, 600), degrees = 15, Token = False): #true = rechts, false = links
        self.camRes = camRes
        self.debugMsg("searching marker {0}".format(offset))
        state = 0
        counter = 0
        hadMarker = False
        #degrees = 15
        while state != -1:
            if state == 0:
                if counter > 6:
                    pendulum = False
                    hadMarker = False
                    self.motor.driveBackward(int(self.maxSpeed), 0, 20)
                if pendulum or hadMarker:
                    direction = not direction
                    counter = counter + 1                                         

                self.debugMsg("state is 0; searching for marker")
                if Token:   
                    wantedMarker = self.lookForToken(offset, direction, degrees)
                else:
                    wantedMarker = self.lookForMarkers(type, offset, direction, degrees)
                
                if wantedMarker != None:
                    self.debugMsg("found expected marker; setting state to 1")
                    degrees = 10
                    hadMarker = True
                    state = 1
                elif wantedMarker !=None and hadMarker == True:
                    self.debugMsg("wanted marker was not found, setting state to 0")
                    state = 0
                    
            elif state == 1:
                self.debugMsg("state is 1, turn to marker")
                if self.turnToMarker(wantedMarker):
                    self.debugMsg("facing marker directly; setting state to 2")
                    state = 2
                else:
                    self.debugMsg("not facing; correcting orientation; state is 0")
                    state = 0
            
            elif state == 2:
                self.debugMsg("state is 2, drive to markers center axis using mk2 routine")
                res = False
                if maxTries > 0:
                    self.debugMsg("we have {0} tries left, attempting mk2 routine".format(maxTries))
                    res = self.driveToCenterAxisMk2(wantedMarker, distMk2)
                    maxTries -= 1
                    if res:
                        self.debugMsg("no correction necessary, setting state to 3")
                        state = 3
                    else:
                        self.debugMsg("corrected, looking again, setting state to 0")
                        state = 0
                else:
                    self.debugMsg("no tries left, setting state to 3")
                    state = 3
                    
            elif state == 3:
                if useMk1:
                    self.debugMsg("state is 3, drive to markers center axis, using mk1 routine")
                    if self.driveToCenterAxis(wantedMarker):
                        self.debugMsg("perfectly on center axis, setting state to 4")
                        state = 4
                    else:
                        self.debugMsg("not on center axis, corrected, setting state to 0")
                        state = 0
                else:
                    state = 4
                    
            elif state == 4:
                if self.driveTowardsMarker(wantedMarker, dist):
                    self.debugMsg("we are now in our wanted position; exiting main loop; state is -1")
                    state = -1
                else:
                    self.debugMsg("our distance to our marker was too damn high; drove forward; state is 0")
                    state = 0
        
        return wantedMarker
        
    def driveToFixpoint(self, type, offset = -1, direction = False):
        state = 0
        degrees = 10
        while state != -1:
            if state == 0:
                wantedMarker = self.lookForMarkers(type, offset, direction, degrees)
                if wantedMarker != None:
                    state = 1
                    degrees = 10
                else:
                    state = 0
                    degrees += 10
                    direction = not direction
            
            elif state == 1:
                if self.turnToMarker(wantedMarker):
                    state = 2
                else:
                    state = 0
            
            elif state == 2:
                if self.driveToCenterAxis(wantedMarker):
                    state = -1
                else:
                    state = 0
        return wantedMarker
        
    def lookAtArena(self, type, offset = 3, direction = False, camRes = (1280, 960)):
        state = 0
        degrees = 20
        self.camRes = camRes
        while state != -1:
            if state == 0:
                wantedMarker = self.lookForMarkers(type, offset, direction, degrees)
                if wantedMarker == None:
                    self.debugMsg("wanted marker was not found, setting state to 0")
                    state = 0
                else:
                    self.debugMsg("found expected marker; setting state to 1")
                    state = 1
            
            elif state == 1:
                self.debugMsg("state is 1, turn to marker")
                if self.turnToMarker(wantedMarker):
                    self.debugMsg("facing marker directly; setting state to 2")
                    state = -1
                else:
                    self.debugMsg("not facing; correcting orientation; state is 0")
                    state = 0
        return wantedMarker
    def debugMsg(self, message):
        if self.debug != None:
            self.debug.printMsg(message, self)

    def __str__(self):
        return "driver"



