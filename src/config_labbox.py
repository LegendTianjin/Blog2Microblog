'''
Created on Mar 1, 2012
@author: vandana

Configuration Module
'''
import logging

PROJECT_ROOT = "/home/vandana/workspace/Blog2Microblog/"
LOGFILE = PROJECT_ROOT + 'logs/application.log'
logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)