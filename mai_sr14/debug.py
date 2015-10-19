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

import time

class Debug(object):
    def __init__(self):
        self.startTime = time.time()
        self.printMsg("debug message service ready for spamming", "debug")
    
    def getDeltaTime(self):
        return time.time() - self.startTime
        
    def printMsg(self, message, sender = "main"):
        print "{0:0>8.4f} -- {1}: {2}".format(self.getDeltaTime(), str(sender), message)
        
    __call__ = printMsg

