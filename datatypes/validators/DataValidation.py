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


class DataValidation(object):
    BED_TYPE = re.compile(r'bed([1-9][0-9]?)\+?([1-9][0-9]?)?$')
    BIGBED_TYPE = re.compile(r'bigBed([1-9][0-9]?)\+?([1-9][0-9]?)?$')
    FILE_TYPE = ["fasta", "fastq", "bam", "bigwig", "bed", "bigbed", "bedgraph"]
    
    def __init__(self, inputFile, fileType, chromSizesFile, options=None):
        self.inputFile = inputFile
        self.fileType = fileType
        self.chromSizesFile = chromSizesFile
        self.options = options
    
    def validate(self):
        """validate input file format"""
        if self._checkDatatype():
            subtools.validateFiles(self.inputFile, self.chromSizesFile, self.fileType, self.options)
        else:
            raise TypeError("validateFiles cannot validate format {0}. Only the following formats can be validated by this tool: \n{1}\n".format(self.fileType, self.FILE_TYPE))
            
    def _checkDatatype(self):
        if re.match(self.BED_TYPE, self.fileType) or re.match(self.BIGBED_TYPE, self.fileType):
            return True
        elif self.fileType.lower() in self.FILE_TYPE:
            return True
        return False
