# -*- coding: utf-8 -*-
'''
bei jedem reboot von /etc/rc.local aufgerufen
'''

from logger import writeLogMsg
from alarme import sendTelegramMsg, wait_for_cmd

msg = f'##### reboot #####'
writeLogMsg(msg)
sendTelegramMsg(msg)

# loops forever --> start with &
while True:
    cmd = wait_for_cmd()
    print(cmd)
    writeLogMsg(f'-----{cmd}-----')
    sendTelegramMsg(f'echo: {cmd}')
