#!/usr/bin/python

import os
import tempfile

# Internal dependencies
from Gtf import Gtf
from datatypes.validators.GtfValidation import GtfValidation
from datatypes.converters.DataConversion import DataConversion


class GtfStringTie(Gtf):
    def __init__( self, input_gtf_false_path, data_gtf):

        super(GtfStringTie, self).__init__(input_gtf_false_path, data_gtf)
        

    def initSettings(self):
        super(GtfStringTie, self).initSettings()
        self.extraSettings["glyph"] = "JBrowse/View/FeatureGlyph/Segments"
        self.extraSettings["subfeatureClasses"] = "UTR"

    
