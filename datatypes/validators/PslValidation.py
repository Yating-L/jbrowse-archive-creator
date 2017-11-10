#!/usr/bin/python
# -*- coding: utf8 -*-

"""
This class handles the subprocess calls of the different tools used
in HubArchiveCreator
"""

import logging
import os
import subprocess
import sys
import string
import tempfile
import re

from util import subtools
from datatypes.validators.DataValidation import DataValidation


class PslValidation(DataValidation):
    
    def __init__(self, inputFile, fileType, chromSizesFile, options=None):
        super(PslValidation, self).__init__(inputFile, fileType, chromSizesFile, options)
    
    def validate(self):
        """validate input file format"""
        self.pslCheck()
                
    def pslCheck(self):
        subtools.pslCheck(self.inputFile)
