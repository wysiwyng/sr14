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

class MAIDuino(Ruggeduino):
    def init(self):
        self.pin_mode(17, OUTPUT)
        self.pin_mode(16, OUTPUT)
        self.pin_mode(15, OUTPUT)
        self.standby()
    
    #lsb: pin 13, msb: pin 11
    
    def standby(self):                  #mode = 0
        #self.digital_write(17, False)
        self.digital_write(16, False)
        self.digital_write(15, False)
    
    def idle(self):                     #mode = 1
        #self.digital_write(17, False)
        self.digital_write(16, False)
        self.digital_write(15, True)
    
    def attack(self):
        #self.digital_write(17, False)
        self.digital_write(16, True)
        self.digital_write(15, False)            
        
    def score(self):
        #self.digital_write(17, True)
        self.digital_write(16, True)
        self.digital_write(15, True)
    
    def warn_on(self):
        self.digital_write(17, True)
    
    def warn_off(self):
        self.digital_write(17, False)
