#!/usr/bin/python
# -*- coding: utf8 -*-

"""
Class to handle Bam files to UCSC TrackHub
"""

import logging
import os
import shutil

from Binary import Binary
from datatypes.validators.DataValidation import DataValidation
from util import subtools




class Bam(Binary):
    def __init__(self, input_bam_false_path, data_bam):
        super(Bam, self).__init__()
        self.inputFile = input_bam_false_path
        self.trackSettings = data_bam
        self.dataType = "bam"
        self.trackType = "bam"
        

    def validateData(self):
        self.validator = DataValidation(self.inputFile, self.dataType, self.chromSizesFile.name)
        self.validator.validate()

    def createTrack(self):
        #shutil.copy(self.inputFile, self.trackDataURL)
        extension = os.path.splitext(self.trackName)[1]
        if extension != '.bam':
            self.trackName = self.trackName + '.bam'
            self.trackDataURL = os.path.join(self.myBinaryFolderPath, self.trackName)
            #self.trackDataURL = os.path.join(self.myTrackFolderPath, self.trackName)
        shutil.copyfile(self.inputFile, self.trackDataURL) 
        bam_index = subtools.createBamIndex(self.inputFile)
        indexName = os.path.basename(bam_index)
        trackIndexURL = os.path.join(self.myBinaryFolderPath, indexName)
        #trackIndexURL = os.path.join(self.myTrackFolderPath, indexName)
        shutil.copyfile(bam_index, trackIndexURL)  
        self.extraSettings['index'] = indexName

    
    
    
        

