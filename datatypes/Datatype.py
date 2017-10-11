#!/usr/bin/python
# -*- coding: utf8 -*-

"""
Super Class of the managed datatype
"""

import os
import tempfile
import collections
from util import subtools
import logging
import abc
from abc import ABCMeta
from TrackDb import TrackDb
from datatypes.validators.DataValidation import DataValidation


class Datatype(object):
    __metaclass__ = ABCMeta

    chromSizesFile = None
    input_fasta_file = None
    extra_files_path = None
    tool_directory = None

    mySpecieFolderPath = None
    myTrackFolderPath = None
    myBinaryFolderPath = None

    def __init__(self):
        not_init_message = "The {0} is not initialized." \
                           "Did you use pre_init static method first?"
        if Datatype.input_fasta_file is None:
            raise TypeError(not_init_message.format('reference genome'))
        if Datatype.extra_files_path is None:
            raise TypeError(not_init_message.format('track Hub path'))
        if Datatype.tool_directory is None:
            raise TypeError(not_init_message.format('tool directory'))
        self.inputFile = None
        self.trackType = None
        self.dataType = None
        self.trackFileType = None
        self.track = None
        self.trackSettings = dict()
        self.extraSettings = collections.OrderedDict()
        

    @staticmethod
    def pre_init(reference_genome, two_bit_path, chrom_sizes_file,
                 extra_files_path, tool_directory, specie_folder, tracks_folder, binary_folder, track_type):
        Datatype.extra_files_path = extra_files_path
        Datatype.tool_directory = tool_directory

        # TODO: All this should be in TrackHub and not in Datatype
        Datatype.mySpecieFolderPath = specie_folder
        Datatype.myTrackFolderPath = tracks_folder
        Datatype.myBinaryFolderPath = binary_folder

        Datatype.input_fasta_file = reference_genome

        # 2bit file creation from input fasta
        Datatype.twoBitFile = two_bit_path
        Datatype.chromSizesFile = chrom_sizes_file
        Datatype.trackType = track_type
    
    def generateCustomTrack(self):
        self.validateData()
        self.initSettings()
        #Create the track file
        self.createTrack()
        # Create the TrackDb Object
        self.createTrackDb()
        logging.debug("- %s %s created", self.dataType, self.trackName)  

    
    @abc.abstractmethod 
    def validateData(self):
        """validate the input data with DataValidation"""
    
    def initSettings(self):
        #Initialize required fields: trackName, longLabel, shortLable
        self.trackName = self.trackSettings["name"]
        self.trackDataURL = os.path.join(self.myTrackFolderPath, self.trackName)
        if self.trackSettings["label"]:
            self.trackLabel = self.trackSettings["label"]
        else:
            self.trackLabel = self.trackName
        if "trackType" in self.trackSettings and self.trackSettings["trackType"]:
            self.trackType = self.trackSettings["trackType"]
        if self.trackSettings["category"]:
            self.extraSettings["category"] = self.trackSettings["category"]
        if "color" in self.trackSettings and self.trackSettings["color"]:
            self.extraSettings["color"] = self.trackSettings["color"]
        
        
    @abc.abstractmethod
    def createTrack(self):
        """Create the final track file"""

    def createTrackDb(self):
        self.track = TrackDb(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)

    