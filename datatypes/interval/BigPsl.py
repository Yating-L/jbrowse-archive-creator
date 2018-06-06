#!/usr/bin/python

import os
import tempfile
import string

from Interval import Interval
from util.index.DatabaseIndex import DatabaseIndex
from util.index.TrixIndex import TrixIndex
from datatypes.validators.DataValidation import DataValidation
from datatypes.converters.DataConversion import DataConversion


class BigPsl(Interval):
    def __init__(self, input_bigpsl_false_path, data_bigpsl):
    
        super(BigPsl, self).__init__()
        self.inputFile = input_bigpsl_false_path
        self.trackSettings = data_bigpsl
        self.dataType = "bed"
        self.bedFields = 12
        self.extFields = 12
        #self.seqType = None
        self.autoSql = os.path.join(self.tool_directory, 'bigPsl.as')
        
    def initSettings(self):
        super(BigPsl, self).initSettings()
        self.extraSettings["glyph"] = "JBrowse/View/FeatureGlyph/Segments"  


    def validateData(self):
        self.validateOptions = self.getValidateOptions(tab="True", autoSql=self.autoSql)
        self.validator = DataValidation(self.inputFile, self.getValidateType(), self.chromSizesFile.name, self.validateOptions)
        self.validator.validate()

    def createTrack(self):
        self.convertType = self.getConvertType() 
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType, 'blat')
        self.converter.convertFormats()
        self.dataType = self.trackFileType
    
    def getValidateType(self):
        if not self.bedFields or not self.extFields:
            raise Exception("Invalid bigPsl format, no {0} or {1}".format("bedFields", "extFields"))
        return self.dataType + str(self.bedFields) + "+" + str(self.extFields)
    
    def _getSeqType(self):
        with open(self.inputFile, "r") as bigpsl:
            sampleSeq = bigpsl.readline().split()
        if len(sampleSeq) == 25:
            return sampleSeq[-1]
        else:
            return None      
