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

from DataValidation import DataValidation



class Gff3Validation(DataValidation):
    
    def __init__(self, inputFile, fileType, chromSizesFile, options=None):
        super(Gff3Validation, self).__init__(inputFile, fileType, chromSizesFile, options)
    
    def validate(self):
        """validate input file format"""
        if self._removeExtraHeader() > 1:
            print("- Warning: Gff3 created with a modified version of your Gff3 by removing extra headers '##gff-version 3'.")
        return self.inputFile
    
    def _removeExtraHeader(self):
        """
        Remove extra meta line: ##gff-version 3
        """
        valid_gff3_file = tempfile.NamedTemporaryFile(bufsize=0, suffix=".gff3", delete=False)
        valid = open(valid_gff3_file.name, 'w')
        num = 0
        with open(self.inputFile, 'r') as f:
            for line in f:
                if '##gff-version 3' in line:
                    if num == 0:
                        num += 1
                    else:
                        continue
                valid.write(line)
        self.inputFile = valid_gff3_file.name
        return num
