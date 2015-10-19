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

import os, ConfigParser

class ConfigReader(object):
    def __init__(self, path, debug = None):
        self.debug = debug
        self.debugMsg("opening config file and creating configParser")
        self.parser = ConfigParser.ConfigParser()
        cFile = open(os.path.join(path, "mai-bot.cfg"))
        self.debugMsg("config file open, checking config file")
        self.parser.readfp(cFile)
        if not self.parser.has_section("mai-bot-cfg"):
            raise ValueError("invalid config file")
        self.debugMsg("config file is valid, ready to read values")
        cFile.close()

    def getKey(self, key):
        return self.parser.get("mai-bot-cfg", key)
        
    def getMaxSpeed(self):
        if self.parser.has_option("mai-bot-cfg", "max-speed"):
            return self.parser.getint("mai-bot-cfg", "max-speed")
        else:
            return 255
    
    def getMaxSpeedTurn(self):
        if self.parser.has_option("mai-bot-cfg", "max-speed-turn"):
            return self.parser.getint("mai-bot-cfg", "max-speed-turn")
        else:
            return 200
    
    def getDistModifier(self):
        if self.parser.has_option("mai-bot-cfg", "dist-modifier"):
            return self.parser.getint("mai-bot-cfg", "dist-modifier")
        else:
            return 10
            
    def getDistModifierBegin(self):
        if self.parser.has_option("mai-bot-cfg", "dist-mod-begin"):
            return self.parser.getint("mai-bot-cfg", "dist-mod-begin")
        else:
            return 80
            
    def getCamResX(self):
        if self.parser.has_option("mai-bot-cfg", "cam-res-x"):
            return self.parser.getint("mai-bot-cfg", "cam-res-x")
        else:
            return 800
            
    def getCamResY(self):
        if self.parser.has_option("mai-bot-cfg", "cam-res-y"):
            return self.parser.getint("mai-bot-cfg", "cam-res-y")
        else:
            return 600
    
    def getMaxTries(self):
        if self.parser.has_option("mai-bot-cfg", "max-tries"):
            return self.parser.getint("mai-bot-cfg", "max-tries")
        else:
            return 2
    
    def getSafe(self):
        if self.parser.has_option("mai-bot-cfg", "safe"):
            return self.parser.getboolean("mai-bot-cfg", "safe")
        else:
            return False
            
    def getSlots(self):
        if self.parser.has_option("mai-bot-cfg", "slots"):
            return str(self.parser.get("mai-bot-cfg", "slots")).split(",")
        else:
            return ["0", "1", "2", "3"]
    
    def getTokenOrder(self):
        if self.parser.has_option("mai-bot-cfg", "token-order"):
            return str(self.parser.get("mai-bot-cfg", "token-order")).split(",")
        else:
            return ["0","1","2","3"]
    
    def getDebug(self):
        if self.parser.has_option("mai-bot-cfg", "debug"):
            return self.parser.getboolean("mai-bot-cfg", "debug")
        else:
            return False
    #def getStart(self):
     # if self.parser.has_option("mai-bot-cfg", "start"):
      # return self.parser.get("mai-bot-cfg", "start")
       # else:
        # return "nearest"
    
    #def getMaxHeight(self):
     # if self.parser.has_option("mai-bot-cfg", "max-height"):
      # return self.parser.getint("mai-bot-cfg", "max-height")
       # else:
        # return 4
        
            
    def debugMsg(self, message):
        if self.debug != None:
            self.debug.printMsg(message, self)
    
    def __str__(self):
        return "ConfigReader"
