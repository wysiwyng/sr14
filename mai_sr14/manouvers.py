from sr import *
import time, math
from motor import MotorBlockException

class ManouverChainException1(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "chainexception1"

class ManouverChainException2(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "chainexception2"

class ManouverChainException3(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "chainexception3"

class ManouverChainException4(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "chainexception4"

class ManouverChainException5(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "chainexception5"


middleOrientationMarkers = [3, 17, 17, 3]
slotMarkers = [[0, 1, 2, 3], [7, 6, 5, 4], [4, 5, 6, 7], [3, 2, 1, 0]]
wpMarkers = [[27, 7], [21, 13]]
slotAngles = [130, 145, 156, 158]
btrackAngles = [[116, 103, 97, 90], [90, 97, 103, 116]]
slotDist = [230, 300, 380, 465]
zoneDist = [[200, 300, 400, 450], [450, 400, 300, 200]]
zone = [[0, 0, 3, 3], [1, 1, 2, 2], [2, 2, 1, 1], [3, 3, 0, 0]]
markerATOM = [[10, 24], [10, 24], [24, 10], [24, 9]]
markerOMAS = [[24, 10], [10, 24]]
tokenArenaAngles = [133, 43, 40, 121]
#-------------------
anglesMBC_n = [24.89, 8.79, 8.79, 24.89]
distBC_n = [321, 294, 294, 321] 
anglesMBA_n = [62.59, 63.43, 59.42, 50.83]
distBA_n = [304, 291, 256, 348]

def setParams(robot, motor, anticd, lift, debug, function, _speed, _speedTurn):
    global currentZone
    global R
    global m
    global a
    global l
    global d
    global f
    global speed
    global speedTurn
    
    currentZone = robot.zone
    R = robot
    m = motor
    a = anticd
    l = lift
    d = debug
    f = function
    speed = _speed
    speedTurn = _speedTurn
#---------------------
#old working stuff

def turnToken1():
    m.driveForward(170, 0, a.getUsDistance() - 9)
    l.prepareTurnToken()
    d("set back")
    m.driveBackward(speed, 0, 35)
    l.afterTokenTurn()
    time.sleep(0.5)
    
def turnToken2():
    m.driveForward(170, 0, a.getUsDistance() - 9)
    l.prepareTurnToken()
    d("set back")
    m.driveBackward(speed, 0, 35)
    l.afterTokenTurn()
    time.sleep(0.5)
    m.driveForward(170, 0, a.getUsDistance() - 9)
    
    d( "turning token again")
    l.prepareTurnToken()
    d( "set back")
    m.driveBackward(speed, 0, 35)
    l.afterTokenTurn()
    time.sleep(0.5)

def takeToken(marker):
    if marker.info.marker_type == MARKER_TOKEN_SIDE and (marker.orientation.rot_z > 175 or marker.orientation.rot_z < -175):
        turnToken2()
    elif marker.info.marker_type == MARKER_TOKEN_BOTTOM:
        turnToken1()
        
    m.driveForward(160, 0, a.getUsDistance() + 4)
    l.grabToken()
    l.driveHeightAsync()

def driveToWaypoint(currentToken):
    if currentToken == 0 and (R.zone == 0 or R.zone == 2):
        m.turnLeft(speedTurn, 180)
        m.driveForward(speed, 0, 280) #We need to add a realistic value here
        m.turnRight(speedTurn, 90)
       
    elif currentToken == 3 and (R.zone == 1 or R.zone == 3):
        m.turnLeft(speedTurn, 180)
        m.driveForward(speed, 0, 100) #We need to add a realistic value here
        m.turnLeft(speedTurn, 90)
       
    elif currentToken == 0 and (R.zone == 1 or R.zone == 3):
        m.turnLeft(speedTurn, 162)
        m.driveForward(speed, 0, 291) #We need to add a realistic value here
        m.turnRight(speedTurn, 90)
       
    elif currentToken == 3 and (R.zone == 0 or R.zone == 2):
        m.turnRight(speedTurn, 162)
        m.driveForward(speed, 0, 291) #We need to add a realistic value here
        m.turnLeft(speedTurn, 90)
       
    elif currentToken == 2:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 100) #We need to add a realistic value here
        m.turnRight(speedTurn, 90)
    
    elif currentToken == 1:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 100) #We need to add a realistic value here
        m.turnLeft(speedTurn, 90)

def getNextToken(nextToken, lastMove): #the robot should be standing right at a slot when this method is called
    d( "turning back and around")
    m.driveBackward(speed, 0, 100)        
    m.turnRight(speedTurn, 180) #now we should be able to see our orientation marker on the wall somewhere in front of us
    
    d( "trying to search for our orientationMarker")
    if lastMove == "far" and R.zone == 0 or lastMove == "far" and R.zone == 2 or lastMove == "near" and R.zone == 1 or lastMove == "near"and R.zone == 3:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 130)
        m.turnLeft(speedTurn, 90)
    
    elif lastMove == "far" and R.zone == 1 or lastMove == "far" and R.zone == 3 or lastMove == "near" and R.zone == 0 or lastMove == "near" and R.zone == 2:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 130)
        m.turnRight(speedTurn, 90)
    
    elif lastMove == "far-middle" and R.zone == 0 or lastMove == "far-middle" and R.zone == 2 or lastMove == "near-middle" and R.zone == 1 or lastMove == "near-middle"and R.zone == 3:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 40)
        m.turnLeft(speedTurn, 90)
    
    elif lastMove == "far-middle" and R.zone == 1 or lastMove == "far-middle" and R.zone == 3 or lastMove == "near-middle" and R.zone == 0 or lastMove == "near-middle" and R.zone == 2:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 40)
        m.turnRight(speedTurn, 90)
        
    f.driveToMarker(MARKER_ARENA, middleOrientationMarkers[R.zone], True, 135)
    
    if nextToken == 0 and R.zone == 0 or nextToken == 0 and R.zone == 2:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 300)
    
    elif nextToken == 0 and R.zone == 1 or nextToken == 0 and R.zone == 3:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 300)
        
    elif nextToken == 1 and R.zone == 0 or nextToken == 1 and R.zone == 2:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 260)
        m.turnLeft(speedTurn, 90)
        
    elif nextToken == 1 and R.zone == 1 or nextToken == 1 and R.zone == 3:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 260)
        m.turnRight(speedTurn, 90)
    
    elif nextToken == 2 and R.zone == 0 or nextToken == 2 and R.zone == 2:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 200)
        m.turnRight(speedTurn, 90)
        
    elif nextToken == 2 and R.zone == 1 or nextToken == 2 and R.zone == 3:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 200)
        m.turnLeft(speedTurn, 90)
    
    elif nextToken == 3 and R.zone == 0 or nextToken == 3 and R.zone == 2:
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 300)
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, 90)
        
    elif nextToken == 3 and R.zone == 1 or nextToken == 3 and R.zone == 3:
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 300)
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, 90)
 
def driveToSlot(marker, nextSlot, currentToken): #We have picked up the token and are standing at one of our two waypoints
    m.turnLeft(150, 180)
    if currentToken == 0 or currentToken == 1:
        wp = "near"
        dist = 250 - marker.dist + nextSlot * 90
    else:
        wp = "far"
        dist = 250 - marker.dist + (3 - nextSlot) * 90
    
    m.driveForward(speed, 0, dist)
    if wp == "near" and (R.zone == 0 or R.zone == 2) or wp == "far" and (R.zone == 1 or R.zone == 3):
        m.turnLeft(speedTurn, 80)
        direction_ = False
    else:
        m.turnRight(speedTurn, 80)
        direction_ = True
    
    f.driveToMarker(MARKER_SLOT, 70, 32, slotMarkers[R.zone][nextSlot]) #Abstand passt leider noch ned

def driveToSlotMk2(nextSlot, currentToken): #testing purposes only
    if currentToken == 0 or currentToken == 1:
        wp = "near"
        m.turnRight(150, 135)  
        m.driveForward(255, 0, 250)
        marker = f.driveToMarker(MARKER_SLOT, 80, 40, slotMarkers[R.zone][nextSlot], direction = False, camRes=(960,720))
    else:
        wp = "far"
        m.turnRight(150, 160)
        m.driveForward(255, 0, 400)
        marker = f.driveToMarker(MARKER_SLOT, 80, 40, slotMarkers[R.zone][nextSlot], direction = False, camRes=(960,720))    
    f.camRes = (800,600)
    l.releaseToken()

def driveToSlotMk3(nextSlot):
    global currentZone
    if (currentZone == 0 or currentZone == 2):
        if R.zone == currentZone:
            m.turnRight(speedTurn, slotAngles[nextSlot])
            m.driveForward(speed, 0, slotDist[nextSlot])
        else:
            m.turnRight(speedTurn, slotAngles[3 - nextSlot])
            m.driveForward(speed, 0, slotDist[3 - nextSlot])
        direction_ = False
        
    elif (currentZone == 1 or currentZone == 3):
        if R.zone == currentZone:
            m.turnLeft(speedTurn, slotAngles[nextSlot])
            m.driveForward(speed, 0, slotDist[nextSlot])
        else:
            m.turnLeft(speedTurn, slotAngles[3 - nextSlot])
            m.driveForward(speed, 0, slotDist[3 - nextSlot])
        direction_ = True
    marker = f.driveToMarker(MARKER_SLOT, 100, 45, slotMarkers[R.zone][nextSlot], direction = direction_)

def driveToWPASMk1(nextToken, currentSlot): #We are standing at one of the four slots and will now navigate to the next waypoint
    m.driveBackward(speed, 0, 220)
    if nextToken == 0 or nextToken == 1:
        dist = 450 - currentSlot * 90
    else:
        dist = 450 - (3 - currentSlot) * 90
        
    global currentZone
    currentZone = zone[R.zone][nextToken]

    if currentZone == 0:
        marker_ = 27
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, dist)
        direction_ = False
    elif currentZone == 1:
        marker_ = 21
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, dist)
        direction_ = True
    elif currentZone == 2:
        marker_ = 13
        m.turnLeft(speedTurn, 90)
        m.driveForward(speed, 0, dist)
        direction_ = False
    elif currentZone == 3:
        marker_ = 7
        m.turnRight(speedTurn, 90)
        m.driveForward(speed, 0, dist)
        direction_ = True 
    
    return f.driveToMarker(MARKER_ARENA, 150, 100, marker_, direction = direction_)
    
def driveToWPASMk2(nextToken, currentSlot): 
    m.driveBackward(speed, 0, 100) 
    global currentZone
    currentZone = zone[R.zone][nextToken]
    if currentZone == R.zone:                                       #zoneDist = [[200, 300, 400, 450], [450, 400, 300, 200]]
        isZoneOurHome = 0
    else:
        isZoneOurHome = 1                                            #btrackAngles = [[140, 125, 114, 112], [112, 114, 125, 140]]
    
    if currentZone == 0:
        m.turnLeft(speedTurn, btrackAngles[isZoneOurHome][currentSlot])
        marker_ = 27
        direction_ = False
    
    elif currentZone == 1:
        m.turnRight(speedTurn, btrackAngles[isZoneOurHome][currentSlot])
        marker_ = 21
        direction_ = True
        
    elif currentZone == 2:
        m.turnLeft(speedTurn, btrackAngles[isZoneOurHome][currentSlot])
        marker_ = 13
        direction_ = False
    
    elif currentZone == 3:
        m.turnRight(speedTurn, btrackAngles[isZoneOurHome][currentSlot])
        marker_ = 7    
        direction_ = True
    
    f.driveOnMarker(MARKER_ARENA, marker_, direction_)    
    return f.driveToMarker(MARKER_ARENA, 150, 100, marker_, direction = direction_)

def driveToWPAT(lastToken): #we have picked up a token and will now go to our waypoint in order to get to the next slot
    m.driveBackward(speed, 0, 40) #just get a little bit away from the wall
    direction_ = True
    if R.zone == 0 or R.zone == 3:     #[[27, 7], [21, 13]]
        wpTurn = 0
    else:
        wpTurn = 1
        
    if (lastToken == 0 and R.zone == 0) or (lastToken == 3 and R.zone == 3):
        m.turnLeft(speedTurn, 10)
        wpNr = 0
        direction_ = False        
    elif (lastToken == 1 and R.zone == 0) or (lastToken == 2 and R.zone == 3):
        wpNr = 0
        m.turnRight(speedTurn, 80)
        direction_ = True
        
    elif (lastToken == 0 and R.zone == 3) or (lastToken == 3 and R.zone == 0):
        direction_ = True
        wpNr = 1
        m.turnRight(speedTurn, 10)
        
    elif (lastToken == 1 and R.zone == 3) or (lastToken == 2 and R.zone == 0):
        direction_ = False
        wpNr = 1
        m.turnLeft(speedTurn, 80)
        
    return f.driveToMarker(MARKER_ARENA, 150, 100, wpMarkers[wpTurn][wpNr], direction = direction_, useMk1 = True)

def driveToSlotAT(currentToken, nextSlot):
    if currentToken == 0:
        m.turnRight(speedTurn, 100)
        direction_ = True
        
    elif currentToken == 1:
        m.turnRight(speedTurn, 180)
        direction_ = True
        
    elif currentToken == 2:
        m.turnLeft(speedTurn, 180)
        direction_ = False
        
    elif currentToken == 3:
        m.turnLeft(speedTurn, 100)
        direction_ = False
        
    f.driveOnMarker(MARKER_SLOT, slotMarkers[R.zone][nextSlot], direction_)    
    return f.driveToMarker(MARKER_SLOT, 100, 45, slotMarkers[R.zone][nextSlot], direction = direction_)
        
def getNextTargetToken(nextToken): #we are standing at one our waypoints and will search for our next token
    if (nextToken == 1 and (R.zone == 0 or R.zone == 2)):
        m.turnLeft(speedTurn, 70)
        direction_ = False
    elif (nextToken == 1 and (R.zone == 1 or R.zone == 3)):
        m.turnRight(speedTurn, 70)
        direction_ = True
    elif (nextToken == 2 and (R.zone == 0 or R.zone == 2)):
        m.driveBackward(speed, 0, 90)
        time.sleep(0.5)
        m.turnRight(speedTurn, 70)
        direction_ = True
    elif (nextToken == 2 and (R.zone == 1 or R.zone == 3)):
        m.driveBackward(speed, 0, 90)
        time.sleep(0.5)
        m.turnLeft(speedTurn, 70)
        direction_ = False
    elif (nextToken == 3 and (R.zone == 0 or R.zone == 2)):
        m.turnLeft(speedTurn, 90)
        time.sleep(0.5)
        m.driveForward(speed, 0, 90)
        time.sleep(0.5)
        m.turnRight(speedTurn, 70)
        direction_ = True
    elif (nextToken == 3 and (R.zone == 1 or R.zone == 3)):
        m.turnRight(speedTurn, 90)
        time.sleep(0.5)
        m.driveForward(speed, 0, 90)
        time.sleep(0.5)
        m.turnLeft(speedTurn, 70)
        direction_ = False
    
    return f.driveToMarker(MARKER_TOKEN_SIDE, 50, 30, R.zone, direction = direction_)
    
#---------------------------------------------------------------------------------------------
#old malfunctioning stuff

def driveToMarkerOMAT(slotMarker, currentToken):
    if R.zone == 0 or R.zone == 2:
        if currentToken == 0:
            m.turnRight(speedTurn, 165)
            markerOM = markerATOM[R.zone][0]
            direction_ = True
        elif currentToken == 1:
            m.turnLeft(speedTurn, 90)
            markerOM = markerATOM[R.zone][0]
            direction_ = False
        elif currentToken == 2:
            m.turnRight(speedTurn, 90)
            markerOM = markerATOM[R.zone][1]
            direction_ = True
        elif currentToken == 3:
            m.turnLeft(speedTurn, 165)
            markerOM = markerATOM[R.zone][1]
            direction_ = False
        dist = 50 + (3 - slotMarker) * 60
    else:
        if currentToken == 0:
            m.turnLeft(speedTurn, 165)
            markerOM = markerATOM[R.zone][0]
            direction_ = False
        elif currentToken == 1:
            m.turnRight(speedTurn, 90)
            markerOM = markerATOM[R.zone][0]
            direction_ = True
        elif currentToken == 2:
            m.turnLeft(speedTurn, 90)
            markerOM = markerATOM[R.zone][1]
            direction_ = False
        elif currentToken == 3:
            m.turnRight(speedTurn, 165)
            markerOM = markerATOM[R.zone][1]
            direction_ = True
        dist = 50 + (slotMarker) * 60
           
    f.driveOnMarker(MARKER_ARENA, markerOM, direction_, dist)
    return direction_
def driveToMarkerOMAS(nextToken):
    if ((R.zone == 0 or R.zone == 2) and nextToken <= 1) or ((R.zone == 1 or R.zone == 3) and nextToken >= 2):
        m.turnLeft(speedTurn, 80)
        _direction = False
        offset = markerOMAS[0][R.zone / 2]
    else:
        m.turnRight(speedTurn, 80)
        _direction = True
        offset = markerOMAS[1][R.zone / 2]
    
    f.driveOnMarker(MARKER_ARENA, offset, _direction, 150)
    return _direction

#----------------------------------------------------------
#new stuff (still needs to be testet though)

def begin(nextToken):
    m.driveForward(speed, 0, 60)
    time.sleep(0.5)
    if nextToken == 0 and (R.zone == 0 or R.zone == 2):
        d("begin is turning left ###########, nextToken is {0}, R.zone is {1}".format(nextToken, R.zone))
        m.turnLeft(speedTurn, 80)
        return False
    elif nextToken == 1 and (R.zone == 1 or R.zone == 3):
        d("begin is turning left ###########, nextToken is {0}, R.zone is {1}".format(nextToken, R.zone))
        m.turnLeft(speedTurn, 80)
        return False
    else:
        d("begin is turning right ###########, nextTOken is {0}, R.zone is {1}".format(nextToken, R.zone))
        m.turnRight(speedTurn, 80)
        return True
        

def tokenToSlot(nextSlot, currentToken):
    state = 1
    direction = False
    while state != -1:
        if state == 1:
            try:
                d("trying tokentoslot1")
                direction = tokenToSlot1(nextSlot, currentToken)
                state = 2
                d("tokentoslot-state is 2")
            except ManouverChainException1:
                m.driveBackward(speed, 0, 40)
                state = 2
                d("tokentoslot-state is 2")
                direction = not direction
        
        elif state == 2:
            try:
                d("trying tokentoslot2")
                marker = tokenToSlot2(nextSlot, currentToken, direction)
                state = 3
                d("tokentoslot-state is 3")
            except ManouverChainException2:
                m.driveBackward(speed, 0, 40)
                d("state remains unaffected")
                d("tokentoslot-state is 2")
        
        elif state == 3:
            try:
                d("trying tokentoslot3")
                res = tokenToSlot3(nextSlot, currentToken, marker)              #res[direction, alpha, dist, beta]
                state = 4
                d("tokentoslot-state is 4")
            except ManouverChainException3:
                m.driveBackward(speed, 0, 40)
                direction = _direction_
                state = 2
                d("tokentoslot-state is 2")
        
        elif state == 4:
            try:
                d("trying tokentoslot4")
                tokenToSlot4(nextSlot, currentToken, res[0], res[1], res[2])   #*1 ( dreiction)
                state = 5
                d("tokentoslot-state is 5")
            except ManouverChainException4:
                if l.hasToken() == False:
                    m.driveBackward(speed, 0, 70)
                    marker = f.driveToMarker(MARKER_SLOT, 50, 32, R.zone, direction = _direction_, Token = True)
                    takeToken(marker)
                else:
                    m.driveBackward(speed, 0, 40)
                state = 2
                d("tokentoslot-state is 2")
                direction = _direction_                                             #*1
        
        elif state == 5:
            try:
                d("trying tokentoslot5")
                if l.hasToken() == False:
                    d("lost Token; searching")
                    m.driveBackward(speed, 0, 70)
                    marker = f.driveToMarker(MARKER_SLOT, 50, 32, R.zone, direction = _direction_, Token = True)
                    d("found token again")
                    takeToken(marker)
                    state = 2
                    d("setting state again to 2")
                else:
                    tokenToSlot5(nextSlot, _direction_)
                    state = -1
                    d("tokentoslot-state is -1")
                    return True
            except ManouverChainException5:
                state = -1
                d("tokentoslot-state is -1")
                return False
            except MotorBlockException:
                m.driveBackward(speed, 0, 40)
                state = 2
                d("tokentoslot-state is 2")
                
        
def tokenToSlot1(nextSlot, currentToken):                                        #method for navigating to our next desired Slot right after we took a token
    try:
        global currentZone
        currentZone = zone[R.zone][currentToken]
        d("setting currentzone {0}".format(currentZone))
        if currentZone == 0 or currentZone == 2:
            m.turnLeft(speedTurn, tokenArenaAngles[currentToken])
            direction_ = False
            d("turning {0} degrees left".format(tokenArenaAngles[currentToken]))
        else:
            m.turnRight(speedTurn, tokenArenaAngles[currentToken])
            direction_ = True
            d("turning {0} degrees right".format(tokenArenaAngles[currentToken]))
        return direction_
    except MotorBlockException:
        raise ManouverChainException1
    #---------------------------------------------------------------------------Exception1

def tokenToSlot2(nextSlot, currentToken, direction_):
    try:
        if R.zone == 0 or R.zone == 3:
            marker = f.lookAtArena(MARKER_ARENA, 3, direction = direction_)
        else:
            marker = f.lookAtArena(MARKER_ARENA, 17, direction = direction_)
        d("we are looking at the middle ArenaMarker; offset is 3 or 17")
        return marker
        
    except MotorBlockException:
        raise ManouverChainException2
    #---------------------------------------------------------------------------Exception2

def tokenToSlot3(nextSlot, currentToken, marker): 
    try:
        if (currentZone == R.zone and (nextSlot == 0 or nextSlot == 1)) or (currentZone != R.zone and (nextSlot == 2 or nextSlot == 3)):
            beta = abs(marker.orientation.rot_y) - anglesMBC_n[nextSlot]
        else:
            beta = abs(marker.orientation.rot_y) + anglesMBC_n[nextSlot]
        d("calculated beta; beta is {0}".format(beta))
        d("rot y is {0}".format(marker.orientation.rot_y))
        d("marker dist is {0}".format(marker.dist))
        d("distbcn is {0}".format(distBC_n[nextSlot]))
        dist = math.sqrt( distBC_n[nextSlot]**2 + (marker.dist*100)**2 -2 * distBC_n[nextSlot] * marker.dist*100 * math.cos(math.radians(beta))) #AC_n
        d("calculated b = AC_n = distanceToDrive; dist is {0}".format(dist))
        site = (distBC_n[nextSlot]**2 - dist**2 - (marker.dist*100)**2) / (-2 * dist * marker.dist*100)
        d("site for acos is {0}".format(site))
        alpha = math.degrees(math.acos(site))
        d("calculated alpha = degreesToTurn; alpha is {0}".format(alpha))
        global _direction_
        if currentZone == 0 or currentZone == 2:
            _direction_ = True
            m.turnLeft(speedTurn, int(alpha - 8))
            d("turning {0} degrees left".format(alpha))
            return alpha, dist, beta
        else:
            _direction_ = False
            m.turnRight(speedTurn, int(alpha - 8))
            d("turning {0} degrees right".format(alpha))
            return alpha, dist, beta
            
    except MotorBlockException:
        raise ManouverChainException3
    #---------------------------------------------------------------------------Exception3

def tokenToSlot4(nextSlot, currentToken, alpha, dist, beta): 
    try:
        d("driving {0} meters forward".format(dist))
        m.driveForward(speed, 0, int(dist))
        gamma = 180 - alpha - beta
        d("calculated gamma; gamma is {0}".format(gamma))
        if (currentZone == R.zone and (nextSlot == 0 or nextSlot == 1)) or (currentZone != R.zone and (nextSlot == 2 or nextSlot == 3)): #Rate mal - wer hat das verbrochen...
           _lambda = gamma - anglesMBC_n[nextSlot]
        else:
           _lambda = gamma + anglesMBC_n[nextSlot]
        d("calculated lambda, the angle we need to turn so we face the slotmarker; lambda is{0}".format(_lambda))  
        
        if currentZone == 0 or currentZone == 2:
            if _lambda > 50:
                m.turnLeft(speedTurn, int(_lambda) - 30)
            d("turning {0} -10 degrees left".format(_lambda))
            global _direction_
            _direction_ = False
        else:
            if _lambda > 50:
                m.turnRight(speedTurn, int(_lambda) - 30)
            d("turning {0} -10 degrees right".format(_lambda))
            global _direction_
            _direction_ = True
        
    except MotorBlockException:
        raise ManouverChainException4
    #---------------------------------------------------------------------------Exception4

def tokenToSlot5(nextSlot, direction_): 
    try:
        f.driveToSlot(slotMarkers[R.zone][nextSlot], direction_)
        d("ready to place token in slot")
    except SyntaxError:
        raise ManouverChainException5
    #---------------------------------------------------------------------------Exception5

def slotToToken(nextToken, currentSlot):
    state = 1
    direction = False
    while state != -1:
        if state == 1:
            try:
                d("trying slotToToken1")
                direction = slotToToken1(nextToken, currentSlot)
                state = 2
                d("slotToToken-state is 2")
            except ManouverChainException1:
                state = 2
                m.driveBackward(speed, 0, 40)
                d("slotToToken-state is 2")
                direction = not direction
        
        elif state == 2:
            try:
                d("trying slotToToken2")
                marker = slotToToken2(nextToken, currentSlot, direction)
                state = 3
                d("slotToToken-state is 3")
            except ManouverChainException2:
                d("state remains unaffected")
                m.driveBackward(speed, 0, 40)
                d("slotToToken-state is 2")
        
        elif state == 3:
            try:
                d("trying slotToToken3")
                res = slotToToken3(nextToken, currentSlot, marker)
                state = 4
                d("slotToToken-state is 4")
            except ManouverChainException3:
                state = 2
                m.driveBackward(speed, 0, 40)
                d("slotToToken-state is 2")
                direction = _direction_
        
        elif state == 4:
            try:
                d("trying slotToToken4")
                slotToToken4(nextToken, currentSlot, res[0], res[1], res[2])
                state = 5
                d("slotToToken-state is 5")
            except ManouverChainException4:
                state = 5 #weil YOLO
                m.driveBackward(speed, 0, 40)
                d("slotToToken-state is 5 weil yolo")
        
        elif state == 5:
            try:
                d("trying slotToToken5")
                return slotToToken5(nextToken, currentSlot)
                state = -1
                d("slotToToken-state is -1; now preparing to take token")
            except ManouverChainException5:
                d("state remains unaffected")
                m.driveBackward(speed, 0, 40)
                d("slotToToken-state is 5; searching again")
                
def slotToToken1(nextToken, currentSlot):
    try:
        global currentZone
        currentZone = zone[R.zone][nextToken]
        d("setting currentzone {0}".format(currentZone))
        if ((R.zone == 0 or R.zone == 2) and (currentSlot == 0 or currentSlot == 1)) or ((R.zone == 1 or R.zone == 3) and (currentSlot == 2 or currentSlot == 3)):
            m.turnRight(speedTurn, 150)
            return True
            d("turning {0}  degrees right".format(150))
        else:
            m.turnLeft(speedTurn, 150)
            return False
            d("turning {0}  degrees left".format(150))
        
    except MotorBlockException:
        raise ManouverChainException1
    #---------------------------------------------------------------------------exception1
    
def slotToToken2(nextToken, currentSlot, direction_):
    try:
        if R.zone == 0 or R.zone == 3:
            marker = f.lookAtArena(MARKER_ARENA, 3, direction = direction_)
        else:
            marker = f.lookAtArena(MARKER_ARENA, 17, direction = direction_)
        d("we are now looking at the middle ArenaMarker; offset is 3 or 17")
        return marker
        
    except MotorBlockException:
        raise ManouverChainException2
    #---------------------------------------------------------------------------exception2

def slotToToken3(nextToken, currentSlot, marker):
    try:
        if (currentSlot <= 1 and R.zone == currentZone) or (currentSlot >= 2 and R.zone != currentZone):  #...und wer hat das verbrochen
            beta = anglesMBA_n[currentSlot] - abs(marker.orientation.rot_y)
        else:
            beta = anglesMBA_n[currentSlot] + abs(marker.orientation.rot_y)
        d("calculated beta; beta is {0}".format(beta))
        dist = math.sqrt((marker.dist*100)**2 + distBA_n[nextToken]**2 - 2 * marker.dist*100 * distBA_n[nextToken] * math.cos(math.radians(beta)))
        #dist = dist - (dist/7)
        d("calculated b = distToDrive; dist is {0}".format(dist))
        gamma = math.degrees(math.acos((distBA_n[nextToken]**2 - (marker.dist*100)**2 - dist**2)/ (-2 * marker.dist*100 *  dist)))
        d("calculated gamma = degreesToTurn; gamma is {0}".format(gamma))
        if (currentZone == 0 or currentZone == 2):
            d("currentZone is {0}".format(currentZone))
            global _direction_
            _direction_ = False
            m.turnRight(130, int(gamma))
            d("turning {0} degrees right".format(gamma))
            return gamma, dist, beta
        else:
            d("currentZone is {0}".format(currentZone))
            global _direction_
            _direction_ = True
            m.turnLeft(130, int(gamma))
            d("turning {0} degrees left".format(gamma))
            return gamma, dist, beta
        
    except MotorBlockException:
        raise ManouverChainException3
    #---------------------------------------------------------------------------exception3

def slotToToken4(nextToken, currentSlot, gamma, dist, beta):
    try:
        d("driving {0} forward".format(dist))
        m.driveForward(speed, 0, int(dist))
        alpha = 180 - beta - gamma
        d("calculated alpha; alpha is {0}".format(alpha))
        
    except MotorBlockException:
        raise ManouverChainException4
    #---------------------------------------------------------------------------exception4
    
def slotToToken5(nextToken, currentSlot):
    try:
        if R.zone == 0 or R.zone == 2:
            if nextToken == 0 or nextToken == 2:
                direction_ = True
            else:
                direction_ = False
        else:
            if (nextToken == 1 or nextToken == 3):
                direction_ = True
            else:
                direction_ = False
        d("direction is {0}".format(direction_))
        #marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 32, 0, direction = direction_, Token = True)                            #die null muss auf r.zone gesetzt werden
        d("ready to take token")
        #return marker
        return direction_
        
    except MotorBlockException:
        raise ManouverChainException5
    #---------------------------------------------------------------------------exception5
