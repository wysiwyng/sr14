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