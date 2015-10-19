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

from sr import *
import motor, debug, time, lift, voltaged, anticollisiond, configReader, function, manouvers, maiduino
from manouvers import ManouverChainException1, ManouverChainException2, ManouverChainException3, ManouverChainException4, ManouverChainException5

R = Robot.setup()
#------------------------add pre init code here

R.ruggeduino_set_handler_by_fwver("MAIDuino", maiduino.MAIDuino)

d = debug.Debug()
d("pre init phase")

m = motor.Motor("Teensyduino_USB_Serial_12345", d)
m.init()


R.init()
d("main init phase")
#------------------------add init code here

R.ruggeduinos[0].init()
v = voltaged.Voltaged(R, d)
v.daemon = True

l = lift.Lift(R, d)
l.daemon = True

a = anticollisiond.AntiCollisiond(R, d)
a.daemon = True

speed = 255
speedTurn = 145
f = function.Driver(R, m, maxSpeed = speed, maxTurnSpeed = speedTurn, debug = d, camRes = (800,600))

c = configReader.ConfigReader(R.usbkey, d)


#This variable will contain the zone as int in which the robot currently is - 
#so it needs to be updated every time we enter a new zone by the specific method



slots = [0, 1, 2, 3]
tokens = [0, 1, 2, 3]
slots = c.getSlots()
tokens = c.getTokenOrder()
slotMarkers = [[0, 1, 2, 3], [7, 6, 5, 4], [4, 5, 6, 7], [3, 2, 1, 0]]

v.start()
l.start()

l.actionFinished.wait()
time.sleep(0.3)
l.tokenHeight()
time.sleep(0.3)
R.ruggeduinos[0].idle()

R.wait_start()
d("program launched")
#------------------------add methods here

manouvers.setParams(R, m, a, l, d, f, speed, speedTurn)

def runTest():                                  #for testing purposes only
    d("driving lift to token height")
    l.tokenHeight()
    d("driving forward 40cm")
    m.driveForward(speed, 0, 40)
    time.sleep(0.5)
    d("turning left 70 deg")
    m.turnLeft(speedTurn, 70)
    time.sleep(0.5)
    d("driving to token 0")
    marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 30, R.zone, direction = False)
    time.sleep(0.5)
    #manouvers.turnToken()
    d("taking token")
    #manouvers.takeToken()
    time.sleep(0.5)
    d("driving to WP")
    #marker = manouvers.driveToWPAT(0, 3)
    manouvers.driveToSlotAT(0, 3)
    time.sleep(0.5)
    d("driving to slot")
    #manouvers.driveToSlotMk3(3)
    l.releaseToken()
    l.tokenHeightAsync()
    time.sleep(1.5)
    d("now let's try to get back to our WP")
    manouvers.driveToWPASMk2(2, 3)
    time.sleep(0.5)
    manouvers.getNextTargetToken(2)
    time.sleep(0.5)
    d("driving to token 3")
    marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 30, R.zone, direction = False)
    time.sleep(0.5)
    #manouvers.turnToken()
    d("taking token")
    #manouvers.takeToken()
    time.sleep(0.5)
    d("driving to WP")
    #marker = manouvers.driveToWPAT(2, 1)
    manouvers.driveToSlotAT(2, 1)
    time.sleep(0.5)
    d("driving to slot")
    #manouvers.driveToSlotMk3(1)
    l.releaseToken()
    l.tokenHeightAsync()

def runSafe():
    token = tokens.pop(0)
    d("popping first slot out of se list {0}".format(token))
    d("calling runPrepare({0})".format(token))
    direction_ = manouvers.begin(token) #muss currentzone setzen; fahrt token aus start aus an und anschliessend den slot
    marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 32, R.zone, direction = direction_, Token = True)
    manouvers.takeToken(marker)
    slot = slots.pop(0)
    d("popping first slot out of se list {0}".format(slot))
    d("calling drivetowpat({0})".format(token))
    manouvers.driveToWPAT(token)
    d("now calling main routine hansalbert") #Yannick was here
    while True:                                 #sei aktuell; token:0 / slot:0
        d("now driving to slot {0}".format(slot))
        manouvers.driveToSlotMk3(slot)          # slot ist 0; token ist 0
        l.releaseToken()
        l.tokenHeight()
        token = tokens.pop(0)                   
        d("popping token out of se list {0}".format(token))
        d("now calling drivetowpasmk2({0},{1})".format(token, slot))
        manouvers.driveToWPASMk2(token, slot)   # slot ist 0; token ist 1
        d("now calling getnexttargettoken({0})".format(token))
        marker = manouvers.getNextTargetToken(token)     # slot ist 0; token ist 1
        slot = slots.pop(0)
        d("popping slot out of se list {0}".format(slot))
        manouvers.takeToken(marker)                 
        
        d("now calling drivetowpat({0})".format(token))
        manouvers.driveToWPAT(token)            # slot ist 1; token ist 1
        #Schuhe.binden()
        
def runFastTest():
    d("driving lift to token height")
    l.tokenHeight()
    d("driving forward 40cm")
    m.driveForward(speed, 0, 40)
    time.sleep(0.5)
    d("turning left 70 deg")
    m.turnLeft(speedTurn, 70)
    time.sleep(0.5)
    d("driving to token 0")
    marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 30, R.zone, direction = False)
    time.sleep(0.5)
    #manouvers.turnToken()
    d("taking token")
    #manouvers.takeToken()
    time.sleep(0.5)
    dir1 = manouvers.driveToMarkerOMAT(0, 0)
    f.driveToMarker(MARKER_SLOT, 50, 34, R.zone, direction = dir1)
    l.releaseToken()
    l.tokenHeightAsync()
    time.sleep(1.5)
    dir2 = manouvers.driveToMarkerOMAS(1)
    f.driveToMarker(MARKER_ARENA, 120, 100, R.zone, direction = dir2)

def runfinal():
    #starting
    #stabding in fron of first token
    #....starting main loop
    nextSlot = 0
    currentToken = 0
    try:
        manouvers.tokenToSlot1(nextSlot, currentToken)
    except ManouverChainException1:
        #blub
        pass
    except ManouverChainException2:
        #blub
        pass
    except ManouverChainException3:
        #blub
        pass
    except ManouverChainException4:
        #blub
        pass
    except ManouverChainException5:
        #blub
        pass
        
def runfinalfinal(): #Because - you know - programers don't have to be creative, so extending the name by itself is totaly fine ^.^  -- also recursive xDD
    token = int(tokens.pop(0))
    d("new token is {0}".format(token))
    l.tokenHeight()
    direction_ = manouvers.begin(token)
    while True:
        d("looking for new token-----------------------------------------------------")
        marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 32, R.zone, direction = direction_, Token = True) ######offset muss r.zone sein
        manouvers.takeToken(marker)
        if token == 0:
            m.driveBackward(speed, 0, 80)
        else:
            m.driveBackward(speed, 0, 40)
        while l.hasToken() == False:
            marker = f.driveToMarker(MARKER_TOKEN_SIDE, 50, 32, R.zone, pendulum = True, direction = direction_, Token = True)
            manouvers.takeToken(marker)    
        time.sleep(0.5)
        try:
            slot = int(slots.pop(0))
        except IndexError:
            l.tokenHeight()
            d("returning; no more slots in list--------------------------------------------------------------------------")
            return
        if(manouvers.tokenToSlot(slot, token) == False):
            #driveToAnotherSlot
            try:
                otherSlot = slotMarkers[R.zone][int(slots.pop(0))]
                d("otherSlot is {0}".format(otherSlot))
            except IndexError:
                l.releaseToken()
                return
            m.driveBackward(speed, 0, 100)
            if (slot > otherSlot and (R.zone == 0 or R.zone == 2)) or (slot < otherSlot and (R.zone == 1 or R.zone == 3)): #Slot zum Ausweichen links
                direction_ = False
                d("looking for a new slot to the left")
            else:                                                                                                       #Slot zum Ausweichen rechts
                direction_ = True
                d("looking for a new slot to the right")
            f.driveToMarker(MARKER_SLOT, 50, 32, otherSlot, direction = direction_)
        tempMarker = f.lookForSlot(slotMarkers[R.zone][slot])
        #if tempMarker != None:
        #    if tempMarker.dist*100 < 40:
        #        d("found one slotmarker; offset is {0}; distance is {1}".format(tempMarker.info.offset, tempMarker.dist))
        #        m.driveBackward(170, 0, 40 - tempMarker.dist*100)
        #else:
        #    d("-------found no slotmarker--------")
        R.ruggeduinos[0].score()
        d("score---------------------------------------------------------------------------------------------------------")
        l.releaseToken()
        time.sleep(1)
        R.ruggeduinos[0].attack()
        l.tokenHeightAsync()
        m.driveBackward(speed, 0, 60)
        time.sleep(1)
        try:
            token = int(tokens.pop(0))
        except IndexError:
            d("returning; no more tokens in list-------------------------------------------------------------------------")
            l.driveHeight()
            return
        #marker = des da unten
        direction_ = manouvers.slotToToken(token, slot)
        #manouvers.takeToken(marker)
        #.........
    
def finalDestination():
    pass
def finalCountdown():# lalalalala
    pass
#------------------------add main code here
#EXPLODE
d("starting")
d.__init__()
R.ruggeduinos[0].attack()


if c.getSafe():
    d("---------------------now running in safe mode---------------------------")
    runSafe()
else:
    d("---------------------now running in yolo mode---------------------------")
    runfinalfinal()

R.ruggeduinos[0].score()
m.driveBackward(255, 0, 100)
m.turnLeft(255, 0)




