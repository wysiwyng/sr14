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

