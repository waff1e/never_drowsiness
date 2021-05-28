import os
import os.path
from os import path

if (path.exists("hrate.txt") == True):
    os.system('python3 app_test_real.py')
else:
    os.system('python3 app_cal_hr.py')