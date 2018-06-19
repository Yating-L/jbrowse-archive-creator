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
from tracks.HTMLFeatures import HTMLFeatures
from tracks.CanvasFeatures import CanvasFeatures
from tracks.BamFeatures import BamFeatures
from tracks.BigwigFeatures import BigwigFeatures
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
    
    trackType = None

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
    def pre_init(reference_genome, chrom_sizes_file,
                 extra_files_path, tool_directory, specie_folder, tracks_folder, binary_folder, track_type):
        Datatype.extra_files_path = extra_files_path
        Datatype.tool_directory = tool_directory

        # TODO: All this should be in TrackHub and not in Datatype
        Datatype.mySpecieFolderPath = specie_folder
        Datatype.myTrackFolderPath = tracks_folder  # temporary raw data files
        Datatype.myBinaryFolderPath = binary_folder

        Datatype.input_fasta_file = reference_genome

        # 2bit file creation from input fasta
        #Datatype.twoBitFile = two_bit_path
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
        if self.trackSettings["long_label"]:
            self.trackLabel = self.trackSettings["long_label"]
        else:
            self.trackLabel = self.trackName
        if "trackType" in self.trackSettings and self.trackSettings["trackType"]:
            self.trackType = self.trackSettings["trackType"]
        if self.trackSettings["group_name"]:
            self.extraSettings["category"] = self.trackSettings["group_name"]
        if "track_color" in self.trackSettings and self.trackSettings["track_color"]:
            self.extraSettings["color"] = self.trackSettings["track_color"]
        #store information of whether to generate name index for the track
        self.extraSettings["nameIndex"] = self.trackSettings["nameIndex"]
        
        
    @abc.abstractmethod
    def createTrack(self):
        """Create the final track file"""

    def createTrackDb(self):
        if self.trackType == 'HTMLFeatures':
            self.track = HTMLFeatures(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)
        elif self.trackType == "CanvasFeatures":
            self.track = CanvasFeatures(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)
        elif self.trackType == "bam":
            self.track = BamFeatures(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)
        elif self.trackType == "bigwig":
            self.track = BigwigFeatures(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)
        else:
            logging.error("Cannot createTrackDb, because trackType is not defined or invalid! trackType = %s", self.trackType)
        self.track.createTrackDb()
            
        #self.track = TrackDb(self.trackName, self.trackLabel, self.trackDataURL, self.trackType, self.dataType, self.extraSettings)

    