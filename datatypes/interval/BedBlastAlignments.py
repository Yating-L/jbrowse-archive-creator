#!/usr/bin/python

import os
import tempfile
import string

from BigPsl import BigPsl
from datatypes.converters.DataConversion import DataConversion
from util import subtools


class BedBlastAlignments( BigPsl ):
    def __init__(self, input_bed_blast_alignments_false_path, data_bed_blast_alignments):

        super(BedBlastAlignments, self).__init__(input_bed_blast_alignments_false_path, data_bed_blast_alignments)
        #self.seqType = 1
        self.trackType = "G-OnRamp_plugin/BlastAlignment"

    def initSettings(self):
        super(BedBlastAlignments, self).initSettings()
        self.extraSettings["subfeatureClasses"] = "match_part"

    
    
    