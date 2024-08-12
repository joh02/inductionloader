#!/usr/bin/python3
# -*- coding: utf-8 -*-
VER = '20240224_220747'

# batCharge_main_module

import signal
import sys

from ceboConst import CeboPortPin, gCebo, initCebo, sFaktAnal
from time import sleep
from state import *
from alarme import sendTelegramMsg
from logger import writeLogMsg

# Konstanten
ALGO = 'charge1hInf'
# ALGO = 'chargeUntilEmptyInf'
# ALGO = 'chargeUntil_B1_Empty'
# ALGO = 'nts_test'

TMESS = 600  # 10 Minuten Zeit zwischen den Messungen
TCYCL = 3600  # s feste Zykluszeit 1h zwischen Umschalten der Batterien
VERB = False  # verboses loggen
B1, B2, B3, B4 = 'B1', 'B2', 'B3', 'B4'
ANZMESS = 4  # Anzahl der Messungen zur MW Bildung bei der Spannungsmessung

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print('laufen wir auf RPi?')
    sys.exit()


###############################################################################
class Connection():
    """
    z.B. K1 von D2 nach B1n, Quelle B1, Kontakt mit RPi Zero W ports
    """

    def __init__(self, name=None, von=None, nach=None, quelle=None, GPIOpin=None, delay=0):
        self.name = name
        self.von = von
        self.nach = nach
        self.quelle = quelle  # Batt. die entladen wird
        self.GPIOpin = GPIOpin  # bei Benutzung der zero-w pins zur Relais Ansteuerung
        self.delay = delay

        if self.GPIOpin:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.GPIOpin, GPIO.OUT)

    def __repr__(self):
        return f'{self.name} ({type(self)})'

    def on(self):
        '''schaltet mich ein'''
        if VERB:
            writeLogMsg(f'switch {self.name} ON')
        GPIO.output(self.GPIOpin, GPIO.HIGH)
        return True

    def off(self):
        '''schaltet mich aus'''
        if VERB:
            writeLogMsg(f'switch {self.name} OFF')
        GPIO.output(self.GPIOpin, GPIO.LOW)
        return True


K1 = Connection(name='K1', von='D2', nach='B1n', quelle='B1', GPIOpin=14, delay=0)
K2 = Connection(name='K2', von='D2', nach='B2n', quelle='B2', GPIOpin=17, delay=0)
K3 = Connection(name='K3', von='D2', nach='B3n', quelle='B3', GPIOpin=27, delay=0)
K4 = Connection(name='K4', von='D2', nach='B4n', quelle='B4', GPIOpin=22, delay=0)

K5 = Connection(name='K5', von='D1', nach='B1p', quelle='B1', GPIOpin=5, delay=0)
K6 = Connection(name='K6', von='D1', nach='B2p', quelle='B2', GPIOpin=6, delay=0)
K7 = Connection(name='K7', von='D1', nach='B3p', quelle='B3', GPIOpin=13, delay=0)
K8 = Connection(name='K8', von='D1', nach='B4p', quelle='B4', GPIOpin=19, delay=0)

K11 = Connection(name='K11', von='S2', nach='B3n', quelle='B4', GPIOpin=26, delay=0)
K12 = Connection(name='K12', von='S2', nach='B4n', quelle='B1, B2, B3', GPIOpin=18, delay=0)
K13 = Connection(name='K13', von='S1', nach='B1p', quelle='B2, B3, B4', GPIOpin=15, delay=0)
K14 = Connection(name='K14', von='S1', nach='B2p', quelle='B1', GPIOpin=24, delay=0)

K17 = Connection(name='K17', von='B1n', nach='B2p', quelle='B3, B4', GPIOpin=25, delay=0)
K18 = Connection(name='K18', von='B1n', nach='B3p', quelle='B2', GPIOpin=12, delay=0)
K19 = Connection(name='K19', von='B2n', nach='B3p', quelle='B1, B4', GPIOpin=16, delay=0)
K20 = Connection(name='K20', von='B2n', nach='B4p', quelle='B3', GPIOpin=20, delay=0)
K21 = Connection(name='K21', von='B3n', nach='B4p', quelle='B1, B2', GPIOpin=21, delay=0)
K30 = Connection(name='K30', von='G', nach='G*', GPIOpin=23, delay=0)
K40 = Connection(name='K40', von='+12V', nach='P', GPIOpin=11, delay=0) # Optokoppler

allConnections = (K1, K2, K3, K4, K5, K6, K7, K8, K11, K12, K13, K14, K17, K18, K19, K20, K21, K30, K40)


# ------------------------------------------------------------------------------
def toDoku():
    '''
    printed alle Kontakte mit ihren locations
    :return:
    '''
    print('\nRelais, von nach        Pin \n' + 51 * '-')
    for con in allConnections:
        print(f'{con.name}\t{con.von} / {con.nach:16}\tGPIOpin: {con.GPIOpin}')


# ------------------------------------------------------------------------------
# Zuordnung Batterie zu Meßkontakte für Leerlaufspannungsmessung (alle anderen AUS !!)
Bat2MessKontaktNr = {
    'B1': (K1, K5),
    'B2': (K2, K6),
    'B3': (K3, K7),
    'B4': (K4, K8)
}

# welcher Kontakt / Relais ist zu schalten, um Batterie Bx als Quelle und den Rest als
# zu ladende zu erhalten, Variante 4 Batterien:
kontaktToSwitch4 = {
    'B1': (K1, K5, K12, K14, K19, K21),  #
    'B2': (K2, K6, K12, K13, K18, K21),  #
    'B3': (K3, K7, K12, K13, K17, K20),  #
    'B4': (K4, K8, K11, K13, K17, K19),  #
    'LT': (K1, K2, K3, K4, K5, K6, K7, K8, K11, K12, K13, K14, K17, K18, K19, K20, K21),  # "Lampentest"
    'off': ()  #
}


# ------------------------------------------------------------------------------
def switchAllKoff():
    for K in allConnections:
        K.off()
    sleep(0.2)
    return True


# ------------------------------------------------------------------------------
def switchK4Bat(drainBat):
    '''schaltet die für drainBat (Batterie die entladen wird) nötigen Kontakte
    :param drainBat: Eintrag in kontaktToSwitch4
    '''
    # zur Sicherheit alle Relais abschalten und 200ms warten:
    switchAllKoff()
    sleep(0.2)
    for K in kontaktToSwitch4[drainBat]:
        K.on()
    K30.on()
    sleep(0.2)
    return True

# ------------------------------------------------------------------------------
def pulsK40(pw=20):
    '''legt Spannungsimpuls in ms an gate des Zündspulen-FET's'''
    K40.on()
    sleep(pw/1000) # pw in ms
    K40.off()
    return

# ------------------------------------------------------------------------------
def pulsK40con(n=1, ph=20, pl=80):
    '''
    :param n: Anzahl Pulse
    :param ph: high Zeit in ms
    :param pl: low Zeit in ms
    :legt n Spannungsimpulse in ms an gate des Zündspulen-FET's
    '''
    for _ in range(n):
        K40.on()
        sleep(ph/1000) # pw in ms
        K40.off()
        sleep(pl/1000)
    return

# ------------------------------------------------------------------------------
def oszitest(bat='B3'):
    '''legt Spannung der drainBat an den Oszillator'''
    switchK4Bat(bat)
    K30.on()


LEDpin = CeboPortPin(19)


# ------------------------------------------------------------------------------
def blinker3(pin=LEDpin):
    '''
    optisches alive Signal
    :param pin: the cebo pin the LED is connected to
    '''
    print('blinker')
    for _ in range(3):
        pin.on()
        sleep(0.1)
        pin.off()
        sleep(0.2)
    return True


# ------------------------------------------------------------------------------
def getAnalogVals(prn=False):
    '''
    Messreihenfolge: 4x 0,1,2,3,4,5
    :param prn:
    :return: Liste der Mittelwerte
    '''
    retList = [0., 0., 0., 0., 0., 0.]
    for nr in range(ANZMESS):
        for ch in range(6):
            valOk = False
            for _ in range(3):
                # falls Cebo abgestürzt ist (OSError:)
                try:
                    global gCebo
                    # nur pos. Werte und skalieren:
                    voltageValue = max(gCebo.device.getSingleEndedInputs()[ch].read(), 0.0) * sFaktAnal
                    valOk = True
                except OSError:
                    gCebo.device.close()  # faule Instanz schließen und neue anlegen
                    sleep(0.1)
                    gCebo = initCebo()
                    msg = f'#### gCebo -Restart Nr {_} ###'
                    writeLogMsg(msg)
                    sendTelegramMsg(msg)
                    sleep(0.1)
                if valOk:
                    break
            retList[ch] += voltageValue
    return [val / ANZMESS for val in retList]



# ------------------------------------------------------------------------------
def geptAnalogVals(prn=False):
    '''
    Messreihenfolge: 4x 0,1,2,3,4,5
    :param prn:
    :return: Liste der Mittelwerte
    '''
    retList = [0., 0., 0., 0., 0., 0.]
    for nr in range(ANZMESS):
        for ch in range(6):
            valOk = False
            for _ in range(3):
                # falls Cebo abgestürzt ist (OSError:)
                try:
                    global gCebo
                    # nur pos. Werte und skalieren:
                    voltageValue = max(gCebo.device.getSingleEndedInputs()[ch].read(), 0.0) * sFaktAnal
                    valOk = True
                except OSError:
                    gCebo.device.close()  # faule Instanz schließen und neue anlegen
                    sleep(0.1)
                    gCebo = initCebo()
                    msg = f'#### gCebo -Restart Nr {_} ###'
                    writeLogMsg(msg)
                    sendTelegramMsg(msg)
                    sleep(0.1)
                if valOk:
                    break
            retList[ch] += voltageValue
    return [val / ANZMESS for val in retList]


# ------------------------------------------------------------------------------
def compareBatX(strBatNr, value=12.2):
    '''
    vergleicht gemessene Bat [1..4] x mit dem value
    :param strBatNr: 'B1'.. 'B4'
    :param value: float Wert der Spannung
    :return: True wenn gemessene Spannung größer als value ist sonst False
    '''
    batIndex = {
        'B1': 0,
        'B2': 1,
        'B3': 2,
        'B4': 3,
    }
    uBats = logMeasAllBat()

    if uBats[batIndex[strBatNr]] > value:
        return True
    else:
        return False


# ------------------------------------------------------------------------------
def measBat(strBatNr):
    '''misst eine Batterie (Kontakte schalten + Messen)'''
    switchAllKoff()
    sleep(0.1)
    # cebo an Batterie schalten mit den entspr. Kontakten:
    for K in Bat2MessKontaktNr[strBatNr]:
        K.on()
    sleep(0.4)
    retVal = getAnalogVals()[0]  # gemessen wird nur mit Kanal 0
    switchAllKoff()
    sleep(0.1)
    return retVal


# ------------------------------------------------------------------------------
def logMeasAllBat():
    '''
    misst alle 4 Batterien und  loggt das
    :return: vektor der Messwerte
    '''
    strToLog = '##>>##;'
    retVals = []
    for strBatNr in (B1, B2, B3, B4):
        val = measBat(strBatNr)
        retVals.append(val)
        strToLog += f'{strBatNr}; {val};    '
    writeLogMsg(strToLog)
    return retVals


# ------------------------------------------------------------------------------
def measAnalInf():
    '''Mess- und Anzeigeschleife für Analogwerte'''
    while True:
        mw = getAnalogVals()
        print(f'{mw[0]:8.2f}\t({mw[1]:8.2f}\t{mw[2]:8.2f}\t{mw[3]:8.2f}\t{mw[4]:8.2f}\t{mw[5]:8.2f})')


# ------------------------------------------------------------------------------
def measBatXinf(bat):
    '''Mess- und Anzeigeschleife für Bat x'''
    try:
        K30.off()
        for K in Bat2MessKontaktNr[bat]:  # cebo an Batterie schalten
            K.on()
        measAnalInf()
    except KeyboardInterrupt:
        switchAllKoff()


# ------------------------------------------------------------------------------
def cleanup():
    '''beim Beenden (egal aus welchem Grund) alles ausschalten'''
    switchAllKoff()
    # gCebo.device.close()
    writeLogMsg('\n----------- cleanup ----- logging stopped  --------')
    print('')  # get a newline
    return


# ------------------------------------------------------------------------------
def handle_sigterm(signum, frame):
    '''Ctrl-D abfangen um noch ein cleanup machen zu können'''
    print("SIGTERM received. Cleaning up and switch all K's off...")
    cleanup()


signal.signal(signal.SIGTERM, handle_sigterm)  # vorstehende Funktion beim OS registrieren


# ------------------------------------------------------------------------------
def ibTool():
    '''REPL zur Inbetriebnahme'''
    # while True:
    #     cmd = input('? ')
    #     if 'Q' == cmd.upper():
    #         break
    #     try:
    #         print(exec(cmd, globals(), locals()))
    #     except Exception as e:
    #         print("", e)
    print('ibTool, so starten: python3 -i main.py   # keine BatNr')


# -- nts: name to state Tabellen  ("state chains") -----------------------------
nts_test = {
    #             name  funcWSB  params  funcAction         params          next      altNext
    "st1": State("st1", go, [], K30.on, [], "st2", None),
    "st2": State("st2", go, [], switchK4Bat, ['B1'], "st3", None),
    "st3": State("st3", wait_ms, [5000], doNothing, [], "st4", None),
    "st4": State("st4", wait_ms, [1000], switchK4Bat, ['B2'], "st5", None),
    "st5": State("st5", wait_ms, [3000], doNothing, [], "st6", None),
    "st6": State("st6", go, [], getAnalogVals, [], "st7", None),
    "st7": State("st7", go, [], switchAllKoff, [gCebo], "st8", None),
    "st8": State("st8", go, [], K30.off, [], "end", None)
}

# B1 entladen:
chargeUntil_B1_Empty = {
    "st1": State("st1", go, [], logMeasAllBat, [], "st2", None),  # Startzust. loggen
    "st2": State("st2", go, [], switchK4Bat, ['B1'], "st3", None),  # Bat Konfig herst.
    "st3": State("st3", go, [], K30.on, [], "st4", None),  # Source zuschalten
    "st4": State("st4", wait_s, [TMESS], compareBatX, ['B1', 11.5], "st2", 'st5', log=True),
    # aller 10min prüfen ob Quelle leer ist
    "st5": State("st5", go, [], switchAllKoff, [gCebo], "end", None)  # alles abschalten, Ende
}

ALLOWED_BATTERIES = {'B1': 'st1', 'B2': 'st13', 'B3': 'st9', 'B4': 'st5'}

# discharge cycle inf.:   B1, B4, B3, B2, B1 ...
chargeUntilEmptyInf = {
    "st1": State("st1", writeLogMsg, ['#### B1 entl.:'], switchK4Bat, ['B1'], "st4", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st4": State("st4", wait_s, [TMESS], compareBatX, ['B1', 11.5], "st1", 'st5', log=True),
    # aller TMESS Sek. prüfen ob Quelle leer ist

    "st5": State("st5", writeLogMsg, ['#### B4 entl.:'], switchK4Bat, ['B4'], "st8", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st8": State("st8", wait_s, [TMESS], compareBatX, ['B4', 11.5], "st5", 'st9', log=True),
    # aller TMESS Sek. prüfen ob Quelle leer ist

    "st9": State("st9", writeLogMsg, ['#### B3 entl.:'], switchK4Bat, ['B3'], "st12", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st12": State("st12", wait_s, [TMESS], compareBatX, ['B3', 11.5], "st9", 'st13', log=True),
    # aller TMESS Sek. prüfen ob Quelle leer ist

    "st13": State("st13", writeLogMsg, ['#### B2 entl.:'], switchK4Bat, ['B2'], "st16", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st16": State("st16", wait_s, [TMESS], compareBatX, ['B2', 11.5], "st13", 'st1', log=True),
    # aller TMESS Sek. prüfen ob Quelle leer ist

    "st17": State("st17", writeLogMsg, ['#### Ende ####'], switchAllKoff, [], "end", None, log=True),
    # alles abschalten, Ende, wird erstmal nicht erreicht--> inf loop
}

# discharge cycle inf.:   B1, B4, B3, B2, B1 ... Idee: cronos9
charge1hInf = {
    "st1": State("st1", writeLogMsg, ['#### B1 entl.:'], switchK4Bat, ['B1'], "st4", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st4": State("st4", wait_s, [TCYCL], compareBatX, ['B1', 16.5], "st1", 'st5', log=True),
    # immer nach 1h loggen & weiterschalten (U viel zu groß)

    "st5": State("st5", writeLogMsg, ['#### B4 entl.:'], switchK4Bat, ['B4'], "st8", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st8": State("st8", wait_s, [TCYCL], compareBatX, ['B4', 16.5], "st5", 'st9', log=True),
    # immer nach 1h loggen & weiterschalten (U viel zu groß)

    "st9": State("st9", writeLogMsg, ['#### B3 entl.:'], switchK4Bat, ['B3'], "st12", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st12": State("st12", wait_s, [TCYCL], compareBatX, ['B3', 16.5], "st9", 'st13', log=True),
    # immer nach 1h loggen & weiterschalten (U viel zu groß)

    "st13": State("st13", writeLogMsg, ['#### B2 entl.:'], switchK4Bat, ['B2'], "st16", None, log=True),
    # Startzust. loggen, Bat Konfig herst.
    "st16": State("st16", wait_s, [TCYCL], compareBatX, ['B2', 16.5], "st13", 'st1', log=True),
    # immer nach 1h loggen & weiterschalten (U viel zu groß)

    "st17": State("st17", writeLogMsg, ['#### Ende ####'], switchAllKoff, [], "end", None, log=True),
    # alles abschalten, wird nicht erreicht--> inf loop
}

# Syntax Check aller vorhandenen state chains (nts's):
for nts in (nts_test, chargeUntil_B1_Empty, chargeUntilEmptyInf):
    assert all(state.nextName == "end" or
               state.nextName in nts or
               state.altNextName in nts or
               state.altNextName is None
               for state in nts.values()
               )

ALGOTAB = {'charge1hInf': charge1hInf,
           'chargeUntilEmptyInf': chargeUntilEmptyInf,
           'chargeUntil_B1_Empty': chargeUntil_B1_Empty,
           'nts_test': nts_test
           }

algo = ALGOTAB[ALGO]


# ------------------------------------------------------------------------------
def main():
    writeLogMsg(f'starte Version {VER}', firstTime=True)

    try:
        writeLogMsg('  ' + 10 * '#' + ' logging startet ' + 10 * '#', firstTime=True)
        if gCebo.device:
            blinker3()
            if len(sys.argv) == 2:  # first arg is the BatName
                if sys.argv[1] in ALLOWED_BATTERIES.keys():
                    writeLogMsg('starte mit Bat: {}'.format(sys.argv[1]), firstTime=False)
                    startState = ALLOWED_BATTERIES[sys.argv[1]]
                else:
                    raise KeyboardInterrupt('falsche oder Keine Startbatterie')
                logMeasAllBat()  # Startzustand loggen
                execute_state_chain(algo, startState)
                ...
            elif len(sys.argv) == 1:  # no Batterie --> ibTool
                ibTool()

        else:
            print('kein (physisches) Gerät gefunden! ')
    except KeyboardInterrupt:
        cleanup()


if __name__ == '__main__':
    main()
