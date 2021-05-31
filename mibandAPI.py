#!/usr/bin/env python3

# This script demonstrates the usage, capability and features of the library.

import argparse
import subprocess
import shutil
import time
from datetime import datetime

from bluepy.btle import BTLEDisconnectError
from cursesmenu import *
from cursesmenu.items import *

from miband_api.constants import MUSICSTATE
from miband_api.miband import miband

class mibandAPI:

    def __init__(self, mac_address, authkey):


        MAC_ADDR = mac_address
        # Validate MAC address
        if 1 < len(MAC_ADDR) != 17:
            print("오류:")
            print("  Your MAC length is not 17, please check the format")
            print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
            exit(1)
        
        AUTH_KEY = authkey
            
        # Validate Auth Key
        if AUTH_KEY:
            if 1 < len(AUTH_KEY) != 32:
                print("Error:")
                print("  Your AUTH KEY length is not 32, please check the format")
                print("  Example of the Auth Key: 8fa9b42078627a654d22beff985655db")
                exit(1)

        # Convert Auth Key from hex to byte format
        if AUTH_KEY:
            AUTH_KEY = bytes.fromhex(AUTH_KEY)

        success = False
        while not success:
            try:
                if (AUTH_KEY):
                    self.band = miband(MAC_ADDR, AUTH_KEY, debug=True)
                    success = self.band.initialize()
                else:
                    self.band = miband(MAC_ADDR, debug=True)
                    success = True
                break
            except BTLEDisconnectError:
                print('Connection to the MIBand failed. Trying out again in 3 seconds')
                # TODO: 여러번 시도해보고 연결 실패하면 프로그램 종료하기
                time.sleep(3)
                continue
            except KeyboardInterrupt:
                print("\nExit.")
                exit()

    def initHeartRate(self):
        self.band.initializeHeartRate()

    def loadHeartRate(self):
        return self.band.loadHeartRate()

    def requestHeartRate(self):
        return self.band.sendPingHeartRate()

    def disconnect(self):
        self.band.disconnect()


# 원본 그대로의 코드
    def get_heart_rate(self):
        print ('Latest heart rate is : %i' % self.band.get_heart_rate_one_time())
        #input('Press a key to continue')


    def heart_logger(self, data):
        print ('Realtime heart BPM:', data)


    # Needs Auth
    def get_realtime(self):
        self.band.start_heart_rate_realtime(heart_measure_callback=self.heart_logger)
        input('Press Enter to continue')

 
