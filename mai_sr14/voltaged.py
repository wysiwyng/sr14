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