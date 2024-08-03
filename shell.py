#!/usr/bin/env python
import os
import readline
from pprint import pprint
from qflask import QFlask

app = QFlask()

os.environ['PYTHONINSPECT'] = 'True'
