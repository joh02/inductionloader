# Induction Loader
The aim is to use this script to log and investigate the behavior and measured efficiency of the induction charger HW. 
Mainly in German, as it is localized here. 

## Description

HW: 
- target: Raspberry Pi Zero
- dedicated relays driver board (to get all potentials free)
- 12 bit voltage measurement with CEBO-LC USB module
- DUT: various coils and switching transistors for back EMF generation, big lead acid batteries

SW:
- two threads that handle switching, the state machine, pulse generation and logging
- the user is informed via the Telegram messaging system when a predefined event has occurred (as the charging process runs 24/7)
- run.py: integrates the transferring and starting of the files to the target into the IDE, for maximum convenience
- can ve switched completely to HW-free simulation by setting SIMU switch in meta.py
- conv.py: plots a diagram from the logged data 
