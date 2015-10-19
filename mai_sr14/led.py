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

import time, threading
from sr import *

class Led(threading.Thread):
    def __init__(self, robot, debug = None):
        threading.Thread.__init__(self)
        self.R = robot
        self.d = debug
        self.newCommand = threading.Event()
        self.command = ""
    
    def run(self):
        oldCommand = ""
        while(True):
            self.newCommand.wait()
            self.newCommand.clear()
            if self.command == "score":
                time.sleep(1)
                self.command = oldCommand
                self.newCommand.set()
            elif self.command == "attack":
                self.attack()
            elif self.command == "idle":
                self.idle()
            elif self.command == "standby":
                self.standby()
            
            oldCommand = self.command
    
    def attack(self):
        self.R.ruggeduinos[0].attack()
        self.command = "attack"
        
    def score(self):
        self.R.ruggeduinos[0].score()
        self.command = "score"
        self.newCommand.set()
    
    def idle(self):
        self.R.ruggeduinos[0].idle()
        self.command = "idle"
    
    def standby(self):
        self.R.ruggeduinos[0].standby()
        self.command = "standby"
            
