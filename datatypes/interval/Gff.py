#!/usr/bin/python

import os
import tempfile
import abc
import shutil

# Internal dependencies
from Interval import Interval
from datatypes.validators.DataValidation import DataValidation
from datatypes.converters.DataConversion import DataConversion

class Gff(Interval):
    def __init__(self):
        super(Gff, self).__init__()
        self.autoSql = os.path.join(self.tool_directory, 'bigGenePred.as')

    
    def createTrack(self):
        shutil.copyfile(self.inputFile, self.trackDataURL)
    