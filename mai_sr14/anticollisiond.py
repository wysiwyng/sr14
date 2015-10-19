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

import time, threading, event

class AntiCollisiond(threading.Thread):
    def __init__(self, robot, alarmDist = 0, debug = None):
            threading.Thread.__init__(self)
            self.R = robot
            self.debug = debug
            self.alarmDist = alarmDist
            self.USDist = 0
            self.USSensor_tooNear = event.Event()
            self.running = threading.Event()
            
    def run(self):
        while(True):
            self.running.wait()

            self.USDist = int(self.R.ruggeduinos[0].analogue_read(0) / (5.0 / 512) * 2.54)

            if self.USDist < self.alarmDist:
                self.USSensor_tooNear([self, self.USDist])

    def getUsDistance(self, samples = 6):
        if not self.running.isSet():
            temp = []
            for i in range(samples):
                temp.append(int(self.R.ruggeduinos[0].analogue_read(0) / (5.0 / 512) * 2.54))
                self.debugMsg("us reads {0}".format(temp[i]))
            self.USDist = temp[int(samples / 2)]
                
        self.debugMsg("ultrasonic sensor reads a distance of {0}".format(self.USDist))
        return self.USDist

    def debugMsg(self, text):
        if self.debug != None:
            self.debug.printMsg(text, self)
    
    def on(self):
        self.running.set()
        
    def off(self):
        self.running.clear()
    
    def __str__(self):
        return "anticollisiond"
