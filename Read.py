#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class Leer:
    
    def __init__(self):        
        self.reader=SimpleMFRC522()        
        
    def hacer_una_lectura(self):
        #reader = SimpleMFRC522()

        try:
                id = self.reader.read_id()
                uid = self.reader.from_dec_to_hex8(id)                
        finally:                
                GPIO.cleanup()
        return uid
