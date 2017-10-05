#!/usr/bin/python

import os
import shutil
from subprocess import Popen, PIPE
import re

# Internal dependencies
from Binary import Binary
from datatypes.validators.DataValidation import DataValidation



class BigWig(Binary):
    def __init__(self, input_bigwig_path, data_bigwig):
        super(BigWig, self).__init__()
        self.inputFile = input_bigwig_path
        self.trackSettings = data_bigwig
        self.dataType = "bigWig"
        self.trackType= "bigwig"

    def initSettings(self):
        super(BigWig, self).initSettings()
        if 'style' in self.trackSettings:
            self.extraSettings['style'] = self.trackSettings['style']

    def validateData(self):
        self.validator = DataValidation(self.inputFile, self.dataType, self.chromSizesFile.name)
        self.validator.validate()

    
