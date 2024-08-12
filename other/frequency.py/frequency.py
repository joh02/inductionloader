# -*- coding: utf-8 -*-
# Ladeimpulserzeugung mittels Durchlaufen einer Tabelle


import time


# Pulsbreite-Tabelle (1 für HIGH, 0 für LOW)
pulse_width_table = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

# Frequenz
frequency = 20  # Hz
period = 1000 / (len(pulse_width_table) * frequency) # zur Simulation 100 statt 1000
ptr = 0

# Simulation der Pins
led = lambda x: print(x)
port = lambda x: print(x)

while True:
    led(pulse_width_table[ptr])     # Ausgabe des logic levels
    # port(pulse_width_table[ptr])     # Ausgabe des logic levels
    time.sleep(int(period))
    ptr += 1
    if ptr >= len(pulse_width_table):
        ptr = 0
