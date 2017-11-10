#!/usr/bin/python

import os
import tempfile
import logging
import shutil

# Internal dependencies
from Interval import Interval
from datatypes.validators.DataValidation import DataValidation
from datatypes.converters.DataConversion import DataConversion

class Bed(Interval):
    def __init__(self, inputBedGeneric, data_bed_generic):
        super(Bed, self).__init__()
        self.inputFile = inputBedGeneric
        self.trackSettings = data_bed_generic
        self.bedFields = None
        self.extFields = None
        self.dataType = "bed"

    def createTrack(self):
        shutil.copyfile(self.inputFile, self.trackDataURL)

    def validateData(self):
        self.validator = DataValidation(self.inputFile, self.getValidateType(), self.chromSizesFile.name)
        self.validator.validate()
        
    def _getBedFields(self):
        """count number of bed fields for generic bed format"""
        with open(self.inputFile, 'r') as bed:
            l = bed.readline().split()
            return len(l)

    def getValidateType(self):
        if not self.bedFields:
            logging.debug("bedFields is not defined, consider the file as Bed generic format, datatype = bed%s", str(self.bedFields))
            self.bedFields = self._getBedFields()
            return self.dataType + str(self.bedFields)
        elif not self.extFields:
            return self.dataType + str(self.bedFields)
        else:
            return self.dataType + str(self.bedFields) + "+" + str(self.extFields)

    

    

