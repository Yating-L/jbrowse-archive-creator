#!/usr/bin/python

import os
import tempfile

# Internal dependencies
from Gff import Gff
from datatypes.validators.GtfValidation import GtfValidation
from datatypes.converters.DataConversion import DataConversion


class Gtf(Gff):
    def __init__( self, input_gtf_false_path, data_gtf):

        super(Gtf, self).__init__()
        self.inputFile = input_gtf_false_path
        self.trackSettings = data_gtf
        self.dataType = "gtf"

    def initSettings(self):
        super(Gtf, self).initSettings()
        self.extraSettings["glyph"] = "JBrowse/View/FeatureGlyph/Segments"
        self.extraSettings["subfeatureClasses"] = "UTR"

    def createTrack(self):
        self.convertType = self.getConvertType()
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType)
        self.converter.convertFormats()
        self.dataType = self.trackFileType

    def validateData(self):
        self.validator = GtfValidation(self.inputFile, self.dataType, self.chromSizesFile.name)
        self.inputFile = self.validator.validate()

