# -*- coding: utf-8 -*-

import sys

from threading import Lock
from time import sleep
from alarme import sendTelegramMsg
from logger import writeLogMsg
from meta import SIMU, REAL
from SimuObjects import MyFileObject

lock = Lock()

if REAL:
    try:
        from CeboMsrApiPython import LibraryInterface, DeviceType
    except (ModuleNotFoundError, OSError) as e:
        print(f'{e}: laufen wir auf RPi?')
        sys.exit()

# Konstanten
sFaktAnal = 1.5 # MB-Erweiterung der 10V Cebo-Eingänge auf 15V

# direction of Cobo pins (e.g. in mask)
IN=0
OUT=1

# Cebo hat 20 IO's:
portBitNrFromIOnr = {
    #   IO  port, bitPos
    0: (0, 0),
    1: (0, 1),
    2: (0, 2),
    3: (0, 3),
    4: (0, 4),
    5: (0, 5),
    6: (0, 6),
    7: (0, 7),
    8: (1, 0),
    9: (1, 1),
    10: (1, 2),
    11: (1, 3),
    12: (1, 4),
    13: (1, 5),
    14: (1, 6),
    15: (1, 7),
    16: (2, 0),
    17: (2, 1),
    18: (2, 2),
    19: (2, 3)
}


#------------------------------------------------------------------------------
if REAL:
    def initCebo():

        device = None
        try:
            devFound = False
            for _ in range(5):
                # Search for devices ...
                devices = LibraryInterface.enumerate(DeviceType.CeboLC)
                if (len(devices) > 0):
                    device = devices[0] # If at least one has been found, use the first one ...
                    devFound = True
                    break
                sleep(1)
                msg=(f'#### CeboDev not found - Versuch {_+1} ###')
                sendTelegramMsg(msg)
                writeLogMsg(msg)


            if devFound:
                device.open()
                # get and configure digital ports
                dp0 = device.getDigitalPorts()[0]
                dp1 = device.getDigitalPorts()[1]
                dp2 = device.getDigitalPorts()[2]

                # input -> 0, output -> 1
                dp0.setOutputEnableMask(0b11111110)
                dp1.setOutputEnableMask(0b11111111)
                dp2.setOutputEnableMask(0b00001111)

                # Configuration of single ended analog inputs: not necessary
            else:
                print('no Cebo Device found')
                sys.exit()

        except Exception as e:
            print(e)
            sys.exit()

        class Cebo:
            device = None

        Cebo.device = device

        Cebo.dp0    = dp0
        Cebo.dp1    = dp1
        Cebo.dp2    = dp2

        Cebo.portsReadFkt = { 0 : dp0.read,
                              1 : dp1.read,
                              2 : dp2.read
                              }

        Cebo.portsWriteFkt = { 0: dp0.write,
                               1: dp1.write,
                               2: dp2.write
                               }
        return Cebo

if SIMU:
    def initCebo():

        device = MyFileObject([])

        # get and configure digital ports
        dp0 = device.getDigitalPorts()[0]
        dp1 = device.getDigitalPorts()[1]
        dp2 = device.getDigitalPorts()[2]

        # input -> 0, output -> 1
        dp0.setOutputEnableMask(0b11111110)
        dp1.setOutputEnableMask(0b11111111)
        dp2.setOutputEnableMask(0b00001111)

        class Cebo:
            device = None

        Cebo.device = device

        Cebo.dp0 = dp0
        Cebo.dp1 = dp1
        Cebo.dp2 = dp2

        Cebo.portsReadFkt = {0: dp0.read,
                             1: dp1.read,
                             2: dp2.read
                             }

        Cebo.portsWriteFkt = {0: dp0.write,
                              1: dp1.write,
                              2: dp2.write
                              }
        return Cebo


gCebo = initCebo()

###############################################################################
class CeboPortPin():
    """
    Richtung: input -> 0, output -> 1
    """

    def __init__(self, io=None):
        self.port = portBitNrFromIOnr[io][0]
        self.bitNr = portBitNrFromIOnr[io][1]
        self.bitMask = 1 << self.bitNr
        self.name = 'IO-'+str(io)

    def on(self):
        value = gCebo.portsReadFkt[self.port]()
        value |= self.bitMask
        gCebo.portsWriteFkt[self.port](value)

    def off(self):
        value = gCebo.portsReadFkt[self.port]()
        value &= (0b11111111 - self.bitMask)
        gCebo.portsWriteFkt[self.port](value)

# Cebos's IO's
IO_0 = CeboPortPin(0)
IO_1 = CeboPortPin(1)
IO_2 = CeboPortPin(2)
IO_3 = CeboPortPin(3)
IO_4 = CeboPortPin(4)
IO_5 = CeboPortPin(5)
IO_6 = CeboPortPin(6)
IO_7 = CeboPortPin(7)
IO_8 = CeboPortPin(8)
IO_9 = CeboPortPin(9)
IO_10 = CeboPortPin(10)
IO_11 = CeboPortPin(11)
IO_12 = CeboPortPin(12)
IO_13 = CeboPortPin(13)
IO_14 = CeboPortPin(14)
IO_15 = CeboPortPin(15)
IO_16 = CeboPortPin(16)
IO_17 = CeboPortPin(17)
IO_18 = CeboPortPin(18)
IO_19 = CeboPortPin(19)



#------------------------------------------------------------------------------
def readCsPorts():
    '''
    returned gelesene und zusammen geoderte Signatur der Digital Ports 0,1,2
    :return: s.o.
    '''
    p0 = gCebo.portsReadFkt[0]()
    p1 = gCebo.portsReadFkt[1]()
    p2 = gCebo.portsReadFkt[2]()
    return (p2 << 16) | (p1 << 8) | p0

def switchCeboIO_on(portNr, bitNr, tms, lock):
    '''
    :param portNr: 0..2
    :param bitNr: einzuschaltentes Bit
    :param tms: Wartezeit in ms
    :param lock: globales lock
    :return: immer True
    '''
    sleep(tms / 1000)  # ms -> s
    lock.acquire()
    p = gCebo.portsReadFkt[portNr]()  # Abbild lesen
    print(f'gelesen: {hex(p)}') #######################
    p |= (1<<bitNr)  # Bit(s) im Abbild setzen
    print(f'schreibe auf port {portNr}: {hex(p)}') ###########################
    gCebo.portsWriteFkt[portNr](p)  # Abbild zum Port
    lock.release()
    return True

#------------------------------------------------------------------------------
def switchCeboIO_off(portNr, bitNr, tms, lock):
    '''

    :param portNr: 0..2
    :param bitNr: auszuschaltentes Bit
    :param tms: Wartezeit in ms
    :param lock: globales lock
    :return:
    '''
    sleep(tms / 1000)  # ms -> s
    lock.acquire()
    p = gCebo.portsReadFkt[portNr]()  # Abbild lesen
    print(f'gelesen: {hex(p)}') #######################
    p &= ~(1<<bitNr)  # Bit(s) im Abbild resetten
    print(f'schreibe auf port {portNr}: {hex(p)}') ###########################
    gCebo.portsWriteFkt[portNr](p)  # Abbild zum Port
    lock.release()
    return True

#------------------------------------------------------------------------------
def switchCeboK_on(k, tms, lock):
    '''
    schaltet Relais k ein, mehrere wenn k tuple oder list
    :param k: (list/tuple of) Connection class des Schützes/Relais
    :param tms: evtl. Wartezeit in ms
    :param lock: der globale lock für den Zugriff auf gCebo
    :return: immer True
    '''
    if isinstance(k,tuple) or isinstance(k,list):
        for kont in k:
            portNr = kont.port
            bitNr = kont.bitNr
            switchCeboIO_on(portNr, bitNr, tms, lock)
    else:
        portNr = k.port
        bitNr = k.bitNr
        switchCeboIO_on(portNr, bitNr, tms, lock)

    return True

#------------------------------------------------------------------------------
def switchCeboK_off(k, tms, lock):
    '''
    schaltet Relais k aus, mehrere wenn k iterable
    :param k: (list/tuple of) Connection class des Schützes/Relais
    :param tms: evtl. Wartezeit in ms
    :param lock: der globale lock für den Zugriff auf Cebo
    :return: immer True
    '''
    if isinstance(k, tuple) or isinstance(k, list):
        for kont in k:
            portNr = kont.port
            bitNr = kont.bitNr
            switchCeboIO_off(portNr, bitNr, tms, lock)
    else:
        portNr = k.port
        bitNr = k.bitNr
        switchCeboIO_off(portNr, bitNr, tms, lock)

    return True

#------------------------------------------------------------------------------
def switchAllBatOff_Cebo():
    '''
    schaltet alle Kontakte / Batterien über Cebo-IO aus
    :return:
    '''
    print('switchAllBatOff')
    lock.acquire()
    gCebo.dp0.write(0)
    gCebo.dp1.write(0)
    gCebo.dp2.write(0)
    lock.release()
    return True


if __name__ == '__main__':
    ...