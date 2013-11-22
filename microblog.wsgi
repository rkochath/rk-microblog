#!/usr/bin/python
import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/apps/microblog/")
os.environ['DATABASE_URL'] = 'mysql://apps:apps@localhost/apps'

from app import app as application
application.secret_key = 'my flask app'

