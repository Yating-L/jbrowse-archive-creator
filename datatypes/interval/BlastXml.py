#!/usr/bin/python

import os
import tempfile
import string

from Interval import Interval
from datatypes.converters.DataConversion import DataConversion
from util.index.DatabaseIndex import DatabaseIndex
from util import subtools


class BlastXml( Interval ):
    def __init__(self, input_blast_alignments_false_path, data_blast_alignments):

        super(BlastXml, self).__init__()
        self.inputFile = input_blast_alignments_false_path
        self.trackSettings = data_blast_alignments
        self.dataType = "blastxml"
        self.seqType = 2
        #self.trackType = "G-OnRamp_plugin/BlatAlignment"

    def initSettings(self):
        super(BlastXml, self).initSettings()
        self.extraSettings["glyph"] = "JBrowse/View/FeatureGlyph/Segments"
        self.extraSettings["subfeatureClasses"] = "match_part"
        if "database" in self.trackSettings:
            self.database_settings = DatabaseIndex(database=self.trackSettings["database"], seqType=self.seqType).setExtLink()
            self.extraSettings["menuTemplate"] = self.database_settings


    def validateData(self):
        return

    def createTrack(self):
        self.convertType = self.getConvertType() 
        self.converter = DataConversion(self.inputFile, self.trackDataURL, self.chromSizesFile.name, self.convertType)
        self.converter.convertFormats()
        self.dataType = self.trackFileType
    
