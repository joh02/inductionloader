# -*- coding: utf-8 -*-

import requests
import json
import time
import logging
from datetime import datetime
from logger import writeLogMsg

remoteCmd = None
token = "6810577423:AAFhCo0VjJkHM6amhMRkh5hNjT5yiav7rH4"
chatID = '948770936'

allCmds = {'>reboot' : None,
           '>end' : None
          }

update_id = 0

# zum Unterdrücken der ständigen Meldungen der urllib3: Setze das Logging-Level dafür auf 'WARNING'
logging.getLogger("urllib3").setLevel(logging.WARNING)


def sendTelegramMsg(msg):
    '''sendet msg an den chat alarme
    '''
    t = time.gmtime()
    jetzt = f'{t.tm_year}{t.tm_mon:02d}{t.tm_mday:02d}_{t.tm_hour + 1:02d}{t.tm_min:02d}{t.tm_sec:02d}'

    try:
        params = {"chat_id": f"{chatID}", "text": f"iloader: {jetzt}: {msg}"}
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        message = requests.post(url, params=params)
    except Exception as e:
        writeLogMsg(f'##### exception beim Senden mit requests: {e} #########')


def wait_for_cmd():
    '''
    wartet bis eine Telegram Nachricht eingetroffen ist
    :return:
    '''
    cycle = 0

    while True:
        answer = (requests.get(f"https://api.telegram.org/bot{token}/getUpdates"))
        content = answer.content
        dataDict = json.loads(content)

        try:
            msg_ok = dataDict['ok']
            last_update = dataDict['result'][-1]
            global update_id
            new_update_id = last_update['update_id']
            # wenn es ein update gegeben hat:
            if new_update_id > update_id:
                # beim ersten Durchlauf wäre IMMER eine Diff von update_id zum Initialwert 0
                if update_id:
                    rec_cmd = last_update['message']['text']
                    if rec_cmd in allCmds.keys():
                        # print(f'{rec_cmd} accepted')
                        break
                update_id = new_update_id  # mitzählen
        except (IndexError, KeyError) as e: # kann leer sein
            print(f'aufgetreten: {e}')
            rec_cmd = None
        # print(f'cycle: {cycle}')
        cycle += 1
        time.sleep(1)
    return rec_cmd




if __name__ == '__main__':
    # sendTelegramMsg('test3')
    cmd = wait_for_cmd()
    print(f'ende: {cmd}')