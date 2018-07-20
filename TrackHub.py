#!/usr/bin/env python

import os
import subprocess
import shutil
import zipfile
import json
import tempfile
import logging
from mako.lookup import TemplateLookup

from datatypes.Datatype import Datatype
from tracks.TrackStyles import TrackStyles
from util import subtools
from util import santitizer


class TrackHub:
    def __init__(self, inputFastaFile, outputFile, extra_files_path, tool_directory, trackType):

        self.mySpecieFolderPath = None

        # Store intermediate files, will be removed if not in debug mode
        self.myTracksFolderPath = None

        # Store interval files and their tabix index
        self.myFinalTracksFolderPath = None

        # Store binary files: Bam, BigWig
        self.myBinaryFolderPath = None

        self.tool_directory = tool_directory
        self.trackType = trackType
        self.reference_genome = inputFastaFile
        self.genome_name = inputFastaFile.assembly_id
        self.extra_files_path = extra_files_path
        self.outputFile = outputFile
        self.chromSizesFile = None

        
        # Set all the missing variables of this class, and create physically the folders/files
        self.__createAssemblyHub__(extra_files_path=extra_files_path)
        # Init the Datatype 
        Datatype.pre_init(self.reference_genome, self.chromSizesFile,
                          self.extra_files_path, self.tool_directory,
                          self.mySpecieFolderPath, self.myTracksFolderPath, self.myBinaryFolderPath, self.trackType)

        self._prepareRefseq()
        self.trackList = os.path.join(self.mySpecieFolderPath, "trackList.json")
        self._createTrackList()
        if Datatype.trackType == 'HTMLFeatures':
            self.myTrackStyle = TrackStyles(self.tool_directory, self.mySpecieFolderPath, self.trackList)
        self.logger = logging.getLogger(__name__)
        self.nameIndexTrackList = []


    def addTrack(self, trackDbObject):
        if trackDbObject['nameIndex'] == "true":
            self.nameIndexTrackList.append(trackDbObject['trackLabel'])
        if trackDbObject['dataType'].lower() == 'bam':
            subtools.add_track_json(self.trackList, trackDbObject['options'])
        elif trackDbObject['dataType'].lower() == 'bigwig':
            subtools.add_track_json(self.trackList, trackDbObject['options'])
        else: 
            if trackDbObject['trackType'] == 'HTMLFeatures':
                self._customizeHTMLFeature(trackDbObject)
                subtools.flatfile_to_json(trackDbObject['trackDataURL'], trackDbObject['dataType'], trackDbObject['trackType'], trackDbObject['trackLabel'], self.mySpecieFolderPath, trackDbObject['options'])
            # Use Tabix index tracks by default for CanvasFeatures
            # TODO: add support for HTMLFeatures
            else:
                subtools.generate_tabix_indexed_track(trackDbObject['trackDataURL'], trackDbObject['dataType'], trackDbObject['track'], self.myFinalTracksFolderPath)
                subtools.add_track_json(self.trackList, trackDbObject['options'])

    def terminate(self, debug="false"):
        """ Write html file """
        self._indexName()
        if debug.lower() == "false":
            self._removeRaw()
        self._outHtml()
        print "Success!\n"


    def _customizeHTMLFeature(self, trackDbObject):
        if trackDbObject['options']:
            subfeatures = trackDbObject['options'].get('subfeatureClasses')
            feature_color = trackDbObject['options']['feature_color']
            if subfeatures:
                for key, value in subfeatures.items():
                    self.myTrackStyle.addCustomColor(value, feature_color)
            else:
                customizedFeature = santitizer.sanitize_name(trackDbObject['trackLabel'])
                clientConfig = json.loads(trackDbObject['options']['clientConfig'])
                clientConfig['renderClassName'] = customizedFeature
                trackDbObject['options']['clientConfig'] = json.dumps(clientConfig)
                self.myTrackStyle.addCustomColor(customizedFeature, feature_color)
                  
    def _removeRaw(self):
        if os.path.exists(self.myTracksFolderPath):
            shutil.rmtree(self.myTracksFolderPath)

    def _createTrackList(self):
        if not os.path.exists(self.trackList):
            os.mknod(self.trackList)   

    def _prepareRefseq(self):
        subtools.prepare_refseqs(self.reference_genome.false_path, self.mySpecieFolderPath)

    def _indexName(self):
        subtools.generate_names(self.mySpecieFolderPath, self.nameIndexTrackList)
        print "finished name index \n"

    def _outHtml(self):
        mylookup = TemplateLookup(directories=[os.path.join(self.tool_directory, 'templates')],
                                  output_encoding='utf-8', encoding_errors='replace')
        htmlTemplate = mylookup.get_template("display.txt")

        with open(self.outputFile, 'w') as htmlfile:
            htmlMakoRendered = htmlTemplate.render(
            jbrowse_hub_name = self.reference_genome.assembly_id,
            trackList = os.path.relpath(self.trackList, self.extra_files_path)
        )
            htmlfile.write(htmlMakoRendered)

    def __createAssemblyHub__(self, extra_files_path):
        # Get all necessaries infos first
        # 2bit file creation from input fasta
        twoBitFile = tempfile.NamedTemporaryFile(bufsize=0)
        subtools.faToTwoBit(self.reference_genome.false_path, twoBitFile.name)

        # Generate the twoBitInfo
        twoBitInfoFile = tempfile.NamedTemporaryFile(bufsize=0)
        subtools.twoBitInfo(twoBitFile.name, twoBitInfoFile.name)

        # Then we get the output to generate the chromSizes
        self.chromSizesFile = tempfile.NamedTemporaryFile(bufsize=0, suffix=".chrom.sizes")
        subtools.sortChromSizes(twoBitInfoFile.name, self.chromSizesFile.name)

        # We can get the biggest scaffold here, with chromSizesFile
        with open(self.chromSizesFile.name, 'r') as chrom_sizes:
            # TODO: Check if exists
            self.default_pos = chrom_sizes.readline().split()[0]

        # Create the specie folder, use generic name "myHub", to support display JBrowse with Galaxy display application
        mySpecieFolderPath = os.path.join(extra_files_path, "myHub")
        if not os.path.exists(mySpecieFolderPath):
            os.makedirs(mySpecieFolderPath)
        self.mySpecieFolderPath = mySpecieFolderPath

        # Create the folder named 'raw' inside the specie folder to place raw files
        tracksFolderPath = os.path.join(mySpecieFolderPath, "raw")
        if not os.path.exists(tracksFolderPath):
            os.makedirs(tracksFolderPath)
        self.myTracksFolderPath = tracksFolderPath

        # Create the folder tracks into the specie folder
        finalTracksFolderPath = os.path.join(mySpecieFolderPath, "tracks")
        if not os.path.exists(finalTracksFolderPath):
            os.makedirs(finalTracksFolderPath)
        self.myFinalTracksFolderPath = finalTracksFolderPath

        myBinaryFolderPath = os.path.join(mySpecieFolderPath, 'bbi')
        if not os.path.exists(myBinaryFolderPath):
            os.makedirs(myBinaryFolderPath)
        self.myBinaryFolderPath = myBinaryFolderPath
