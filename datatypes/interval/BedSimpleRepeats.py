#!/usr/bin/python

import os
import tempfile

from Bed import Bed
from datatypes.validators.DataValidation import DataValidation
from datatypes.converters.DataConversion import DataConversion


class BedSimpleRepeats( Bed ):
    def __init__(self, input_bed_simple_repeats_false_path, data_bed_simple_repeats):

        super(BedSimpleRepeats, self).__init__(input_bed_simple_repeats_false_path, data_bed_simple_repeats)
        self.bedFields = 4
        self.extFields = 12
        self.autoSql = os.path.join(self.tool_directory, 'trf_simpleRepeat.as')
        self.trackFileType = "gff"

    def validateData(self):
        self.validateOptions = self.getValidateOptions(tab="True", autoSql=self.autoSql)
        self.validator = DataValidation(self.inputFile, self.getValidateType(), self.chromSizesFile.name, self.validateOptions)
        self.validator.validate()
    

    def createTrack(self):
        self.convertType = self.getConvertType()
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType, 'trfbig')
        self.converter.convertFormats()
        self.dataType = self.trackFileType

