# -*- coding: utf-8 -*-
'''
umwandeln des logs in .csv und plotten
'''

import re
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt

inPath = '/home/joh/temp/batCharge.log'
outPath = '/home/joh/temp/batCharge.csv'

outFile = open(outPath, 'w')

#----------------------------------------------------------------------------
def calc_xticks(timestamps):
    # Berechnung der x_ticks
    XNSOLL = 30  # Anzahl der ticks auf der x-Achse bis zu der alle angezeigt werden

    if len(timestamps)>60:
        last_ts, *other = timestamps[-1], timestamps[:-1]
        tf = max(int(len(other[0]) / XNSOLL), 3)  # mind. 4 ticks (3+1)
        x_ticks = other[0][::tf]  # nur XNSOLL viele anzeigen
        x_ticks.append(last_ts)  # letzten immer anzeigen
    else:
        x_ticks = timestamps  # ALLE anzeigen

    return x_ticks

with open(inPath, 'r') as fn:
    lines = fn.readlines()

v_vek = []
# create the .csv:
with open(outPath, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=';')

    # headline for convenience:
    csv_values = ('time', 'Bat1', 'Bat2', 'Bat3', 'Bat4')
    csv_writer.writerow(csv_values)

    for line in lines:
        if '##>>##' in line: # wenn es eine Zeile mit Messwerten ist:
            spl = line.split(';')
            csv_values = (spl[0],
                          spl[3].replace('.',','),
                          spl[5].replace('.', ','),
                          spl[7].replace('.', ','),
                          spl[9].replace('.', ','))
            csv_writer.writerow(csv_values)
            v_vek.append([spl[0], float(spl[3]), float(spl[5]), float(spl[7]), float(spl[9])])

try:
    assert len(v_vek)>0
except AssertionError as e:
    print(f'{e} (AssertionError):   noch nichts geloggt')
    sys.exit(1)  # 1 als Exit-Code für Fehler


# make the plot:
# Erzeuge einen Bereich von Zeit-Werten (x-Achse)
x = np.linspace(-2, 2, len(v_vek))


# Extrahiere die Zeitpunkte und die Daten für die einzelnen Komponenten
timestamps = [entry[0] for entry in v_vek]
float_x_values = [entry[1] for entry in v_vek]
float_y_values = [entry[2] for entry in v_vek]
float_z_values = [entry[3] for entry in v_vek]
float_a_values = [entry[4] for entry in v_vek]

# Plotte die Daten über die Zeit
plt.figure(figsize=(10, 6))

plt.plot(timestamps, float_x_values, label='Bat1')
plt.plot(timestamps, float_y_values, label='Bat2')
plt.plot(timestamps, float_z_values, label='Bat3')
plt.plot(timestamps, float_a_values, label='Bat4')

x_ticks = calc_xticks(timestamps)

plt.xticks(x_ticks, rotation=90)
plt.xlabel(f'Zeit,  ({len(v_vek)} Werte)')
plt.ylabel('V_Bat / V')
plt.title('Topfspule 0,26mH stündlicher Wechsel, Tastverhältnis 0,23')
plt.legend()
plt.grid(True)
plt.tight_layout()  # Für bessere Anzeige mit gedrehten x-Achsentexten


def main():
    plt.show()

if __name__ == '__main__':
    main()
