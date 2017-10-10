#!/usr/bin/python

import os
import tempfile

# Internal dependencies
from Gff import Gff
from datatypes.validators.Gff3Validation import Gff3Validation


class Gff3_mrna( Gff ):
    def __init__(self, input_Gff3_false_path, data_gff3):
        super( Gff3_mrna, self ).__init__()
        self.inputFile = input_Gff3_false_path
        self.trackSettings = data_gff3
        self.dataType = "gff"
        #self.trackType = "G-OnRamp_plugin/GenePred"

    def initSettings(self):
        super(Gff3_mrna, self).initSettings()
        self.extraSettings["type"] = "mRNA"

    def validateData(self):
        self.validator = Gff3Validation(self.inputFile, self.dataType, self.chromSizesFile.name)
        self.inputFile = self.validator.validate()

