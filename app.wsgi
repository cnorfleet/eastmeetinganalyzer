#! /usr/bin/python3.6

import logging
import sys
logging.basicConfig(stream=sys.stderr)
#sys.path.insert(0, '/var/www/dormmeeting.cnorfleet.com/eastmeetinganalyzer/')
sys.path.append('/var/www/dormmeeting.cnorfleet.com/eastmeetinganalyzer/')
from main import app as application

