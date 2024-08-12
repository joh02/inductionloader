# -*- coding: utf-8 -*-
import logging
import time
from meta import SIMU, REAL

if SIMU:
    LOGDIR = './batCharge.log'
if REAL:
    LOGDIR = 'logs/batCharge.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[
                        logging.FileHandler(LOGDIR),  # Ort des logfiles
                        logging.StreamHandler()  # Dieser Handler schreibt in die Konsole
                    ])


#------------------------------------------------------------------------------
def writeLogMsg(msg, firstTime=False):
    '''
    :param msg: the string to be logged
    :param firstTime: emphases this msg as the beginning of a new log while appending to a existing file
    :return: True
    '''
    if firstTime:
        logging.info('\n\n--------------')
    timeStr = time.strftime("%Y%m%d_%H%M%S")
    logging.info(f'{timeStr}; {msg}')
    return True
