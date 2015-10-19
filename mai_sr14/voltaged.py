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

class Voltaged(threading.Thread):
    def __init__(self, R, out, interval = 5):
        threading.Thread.__init__(self)
        self.R = R
        self.out = out
        self.interval = interval
        
    def run(self):
        while True:
            u = self.R.power.battery.voltage
            i = self.R.power.battery.current
            self.out.printMsg("voltage is {0}".format(u), self)
            self.out.printMsg("current is {0}".format(i), self)
            if u < 11.0:
                self.R.power.beep(800, 0.5)
                self.out.printMsg("battery is getting low...", self)
            time.sleep(self.interval)
    
    def __str__(self):
        return "voltaged"
