#!/usr/bin/env python

import RPi.GPIO as GPIO
import urllib.error
import gi
import threading
import urllib.request
import json
#falta el display

class Connection:
    
    '''def __init__(self,uid):
        self.uid=uid'''
        
    def __init__(self):        
        self.uid=""
        
    def set_uid(self, uid):
        self.uid=uid
        print(uid)
        
    def get_uid(self):       
        print(self.uid)
        return self.uid
    
    def login_connection(self):
        try:
            link = 'http://pbetelematica.ml/login?student_id=' + self.uid        
            with urllib.request.urlopen(link) as f:      #.request perquè vull llegir       
                user_name = f.read().decode('utf-8')
        except Exception as err:
            return "error_in_login_instrucction"
        return user_name
        
    
    def menu_connection(self, entry):        
        try:
            wk_uid=self.uid      
            if '?' not in entry:
                link = 'http://pbetelematica.ml/' + entry + '?student_id=' + wk_uid
            else:
                link = 'http://pbetelematica.ml/' + entry + '&student_id=' + wk_uid      
            with urllib.request.urlopen(link) as f:
                json_table= f.read().decode('utf-8')
            return json_table
        except  urllib.error.HTTPError as err: #error d'instrucció no reconeguda
            return "error_in_menu_instrucction"
        
