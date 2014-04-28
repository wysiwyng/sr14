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