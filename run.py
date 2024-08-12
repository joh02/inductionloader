#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time

from meta import TARGET, LOCAL_WORKDIR, REMOTE_DIR

filesToLoad = [
    'main.py',
    'state.py',
    'ceboConst.py',
    'CeboMsrApiPython.py',
    'alarme.py',
    'logger.py',
    'restart.py',
    'meta.py',
    'SimuObjects.py'
    ]



def scpToZeroW(lFiles):
    assert type(lFiles)==list, 'lFiles is not type List'
    if not len(lFiles):
        print('no files to transmit')

    scpCmd = 'scp ' +  ' '.join(lFiles) + f' root@{TARGET}:'+ REMOTE_DIR
    try:
        subprocess.check_output(scpCmd.split())
    except subprocess.CalledProcessError:
        print(f'Kommando {scpCmd}  nicht erfolgreich!')
        sys.exit()

    # check for md5 sums:
    for file_name in lFiles:
        try:
            md5_local = subprocess.run(['md5sum', file_name], capture_output=True, text=True, check=True)
            md5_remote = subprocess.run(['ssh', f'root@{TARGET}',  f'md5sum', f'{REMOTE_DIR}/{file_name}'],
                                        capture_output=True, text=True, check=True)

            md5_local_checksum = md5_local.stdout.split()[0]
            md5_remote_checksum = md5_remote.stdout.split()[0]

            if md5_local_checksum == md5_remote_checksum:
                print(f"{file_name} wurde erfolgreich übertragen.")
            else:
                print(f"Fehler bei der Übertragung von {file_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Überprüfen von {file_name}: {e}")
    return

def insertTimestamp():
    ''' vor dem Kopieren wird der akt timestamp in main.py eingetragen
        damit der beim Starten angezeigt werden kann
    '''
    t=time.gmtime()
    now = f'{t.tm_year}{t.tm_mon:02d}{t.tm_mday:02d}_{t.tm_hour+1:02d}{t.tm_min:02d}{t.tm_sec:02d}'
    print(f'insert timestamp in main.py: {now}')

    # Öffnen Sie die Datei im Schreibmodus
    with open('main.py', 'r') as file:
        lines = file.readlines()

    # in Zeile 3 soll die Version stehen:
    if 'VER =' in lines[2]:
        # Ersetzen Sie die 3. Zeile mit Ihrem gewünschten String
        lines[2] = f"VER = '{now}'\n"

        with open('main.py', 'w') as file:
            file.writelines(lines)
        # schnell noch syncen, damit auch wirklich geschrieben wird
        subprocess.run("sync", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    else:
        print("kein 'VER =' in Zeile 3 von main.py")
        sys.exit()


if __name__ == '__main__':
    insertTimestamp()
    scpToZeroW(filesToLoad)
