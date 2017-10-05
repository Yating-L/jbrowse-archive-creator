import logging
import os
import tempfile

# Internal dependencies
from Interval import Interval
from datatypes.validators.PslValidation import PslValidation
from datatypes.converters.DataConversion import DataConversion


class Psl(Interval):
    def __init__(self, input_psl_path, data_psl):
        super(Psl, self).__init__()
        self.inputFile = input_psl_path
        self.trackSettings = data_psl
        self.dataType = "psl"
        self.trackType = "bigPsl"
        self.autoSql = os.path.join(self.tool_directory, 'bigPsl.as')

    def initSettings(self):
        super(Psl, self).initSettings()
        self.trackName = "".join( ( self.trackName, ".bb") )
        self.trackDataURL = os.path.join(self.myTrackFolderPath, self.trackName)
        if "track_color" in self.trackSettings:
            self.extraSettings["color"] = self.trackSettings["track_color"]
        if "group_name" in self.trackSettings:
            self.extraSettings["group"] = self.trackSettings["group_name"]
        self.extraSettings["visibility"] = "dense"
        self.extraSettings["priority"] = self.trackSettings["order_index"]
    
    def validateData(self):
        self.validator = PslValidation(self.inputFile, self.dataType, self.chromSizesFile)
        self.validator.validate()

    def createTrack(self):
        self.convertType = self.getConvertType()
        self.options = self.getConvertOptions("bed12+12", tab="True", autoSql=self.autoSql, extraIndex="name")
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType, self.options)
        self.converter.convertFormats()

    def getConvertType(self):
        return (self.dataType.lower(), self.trackType.lower())
