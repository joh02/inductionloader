# -*- coding: utf-8 -*-
# Komm zwischen restart.py / alarme.py / main.py

import multiprocessing
import time

def sender(pipe):
    msg = 'msg2'
    pipe.send(msg)
    print(f" send: {msg}")
    time.sleep(1)  # Gib dem Empfänger Zeit, die Pipe zu öffnen

def empfaenger(pipe):
    time.sleep(1)  # Gib dem Sender Zeit, die Pipe zu schreiben
    data = pipe.recv()
    print(f'received: {data}')

if __name__ == '__main__':
    parent_pipe, child_pipe = multiprocessing.Pipe()

    sender_process = multiprocessing.Process(target=sender, args=(child_pipe,))
    receiver_process = multiprocessing.Process(target=empfaenger, args=(parent_pipe,))

    sender_process.start()
    receiver_process.start()

    sender_process.join()
    receiver_process.join()
