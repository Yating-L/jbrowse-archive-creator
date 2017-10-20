#!/usr/bin/python

import os
import tempfile
import logging

# Internal dependencies
from Gff import Gff
from datatypes.validators.Gff3Validation import Gff3Validation


class Gff3( Gff ):
    def __init__(self, input_Gff3_false_path, data_gff3):
        super( Gff3, self ).__init__()
        self.inputFile = input_Gff3_false_path
        self.trackSettings = data_gff3
        self.dataType = "gff"

    def initSettings(self):
        super(Gff3, self).initSettings()
        feature_type = self._checkFeatureType(self.inputFile)
        if feature_type != -1:
            self.extraSettings["type"] = feature_type
            if feature_type == "transcript":
                self.extraSettings["transcriptType"] = "transcript"
        self.extraSettings["subfeatureClasses"] = "CDS"
    
    def validateData(self):
        self.validator = Gff3Validation(self.inputFile, self.dataType, self.chromSizesFile.name)
        self.inputFile = self.validator.validate()

    @staticmethod
    def _checkFeatureType(gff_file):
        TYPES = ["transcript", "mRNA"]
        with open(gff_file, 'r') as f:
            lines = f.readlines()
        for li in lines:
            if "#" not in li:
                feature_type = li.split()[2]
                if feature_type in TYPES:
                    return feature_type
        logging.debug("The type of the feature either transcript or mRNA is not found in Gff3 file")
        return -1

