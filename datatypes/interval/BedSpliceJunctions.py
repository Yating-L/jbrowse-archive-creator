#!/usr/bin/python

import os
import tempfile

from Bed import Bed
from datatypes.validators.DataValidation import DataValidation
from datatypes.converters.DataConversion import DataConversion



class BedSpliceJunctions( Bed ):
    def __init__(self, input_bed_splice_junctions_false_path, data_bed_splice_junctions):

        super(BedSpliceJunctions, self).__init__(input_bed_splice_junctions_false_path, data_bed_splice_junctions)
        self.bedFields = 12
        self.extFields = 1
        self.autoSql = os.path.join(self.tool_directory, 'spliceJunctions.as')
        self.trackFileType = "gff"

    def initSettings(self):
        super(BedSpliceJunctions, self).initSettings()
        self.extraSettings["glyph"] = "JBrowse/View/FeatureGlyph/Segments"
        self.extraSettings["subfeatureClasses"] = "exon_junction"

    def validateData(self):
        self.validateOptions = self.getValidateOptions(tab="True", autoSql=self.autoSql)
        self.validator = DataValidation(self.inputFile, self.getValidateType(), self.chromSizesFile.name, self.validateOptions)
        self.validator.validate()

    def createTrack(self):
        self.convertType = self.getConvertType()
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType, 'regtools')
        self.converter.convertFormats()
        self.dataType = self.trackFileType

