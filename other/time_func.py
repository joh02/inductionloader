import time
import threading

###############################################################################
class ThrSwitchClass (threading.Thread):
    def __init__(self, tms, action):
        '''
        :param tms: time to wait in ms
        :param action: function to call after tms elapsed
        '''
        threading.Thread.__init__(self)
        self. action = action
        self.tms = tms # time to wait in ms
        self.lastTime = time.time()


    def run(self):
        elapsed = False

        while not elapsed:
            self.now = time.time()
            if self.now > self.lastTime + self.tms / 1000: # ms -> s
                elapsed = True
                #self.lastTime = self.now
        self.action()
        return

###############################################################################
class WaitUntilT():
    """
    wait if act. time ist greater then lastTime+T
    aequidistand measurement intervals
    """
    lastTime = 0

    def __init__(self, T):

        self.stamp = WaitUntilT.lastTime = self.now = time.time()
        self.deltaT = T


    def wait(self, retTime=False):
        elapsed = False

        while not elapsed:
            self.now = time.time()
            if self.now > WaitUntilT.lastTime + self.deltaT:
                elapsed = True
                WaitUntilT.lastTime = self.now
                if retTime:
                    return round(self.now-self.stamp, 2)
                else:
                    return None

#------------------------------------------------------------------------------
def getTimeStamp():

    t=time.gmtime()
    stamp = '{}{:02d}{:02d}_{:02d}{:02d}{:02d}'.format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour+1, t.tm_min, t.tm_sec)
    return stamp


if __name__ == '__main__':
    print(time.time())
    w1 = WaitUntilT(3.0)
    print(w1.wait(retTime=False))
    print(time.time())

    print('timeStamp: ', getTimeStamp())