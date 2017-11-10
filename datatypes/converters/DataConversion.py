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

from bedToGff3 import bedToGff3   
from blastxmlToGff3 import blastxmlToGff3 
from gtfToGff3 import gtfToGff3
   



class DataConversion(object):
    CONVERT_OPERATIONS = {("bed", "gff"): "bedtogff3",
                          ("blastxml", "gff"): "blastxmltogff3",
                          ("gtf", "gff"): "gtftogff3"}
    
    def __init__(self, inputFile, outputFile, chromSizesFile, operateType, options=None):
        if not operateType:
            return 
        if not inputFile:
            raise TypeError("the input file is not specified!\n")
        self.inputFile = inputFile
        self.chromSizesFile = chromSizesFile
        self.outputFile = outputFile
        self.operateType = operateType
        self.options = options
        
        
    
    def convertFormats(self):
        """ Convert data into JBrowse track """
        convertMethod = self.CONVERT_OPERATIONS[self.operateType]
        if convertMethod == "bedtogff3":
            bedToGff3(self.inputFile, self.chromSizesFile, self.outputFile, self.options)
        elif convertMethod == "blastxmltogff3":
            blastxmlToGff3(self.inputFile, self.outputFile)
        elif convertMethod == "gtftogff3":
            gtfToGff3(self.inputFile, self.outputFile, self.chromSizesFile)
        else:
            raise ValueError("the operation %s is not defined!\n", self.operateType)
