#!/usr/bin/env python

import os
import subprocess
import shutil
import zipfile
import json
import tempfile
import logging

from datatypes.Datatype import Datatype
from apollo.ApolloInstance import ApolloInstance
from tracks.TrackStyles import TrackStyles
from util import subtools
from util import santitizer


class TrackHub:
    def __init__(self, inputFastaFile, apollo_user, outputFile, extra_files_path, tool_directory, trackType, apollo_host):
        
        self.rootAssemblyHub = None

        self.mySpecieFolderPath = None

        # Store intermediate files, will be removed if not in debug mode
        self.myTracksFolderPath = None

        # Store binary files: Bam, BigWig
        self.myBinaryFolderPath = None

        self.tool_directory = tool_directory
        self.trackType = trackType
        self.reference_genome = inputFastaFile
        self.genome_name = inputFastaFile.assembly_id
        self.extra_files_path = extra_files_path
        self.outputFile = outputFile
        self.chromSizesFile = None

        # Set up apollo
        self.apollo = ApolloInstance(apollo_host)
        self.apollo_user = apollo_user
        
        # Set all the missing variables of this class, and create physically the folders/files
        self.rootAssemblyHub = self.__createAssemblyHub__(extra_files_path=extra_files_path)
        # Init the Datatype 
        Datatype.pre_init(self.reference_genome, self.chromSizesFile,
                          self.extra_files_path, self.tool_directory,
                          self.mySpecieFolderPath, self.myTracksFolderPath, self.myBinaryFolderPath, self.trackType)  

        self._prepareRefseq()
        self.trackList = os.path.join(self.mySpecieFolderPath, "trackList.json")
        self._createTrackList()
        
        self.myTrackStyle = TrackStyles(self.tool_directory, self.mySpecieFolderPath, self.trackList)
        #self.cssFolderPath = os.path.join(self.mySpecieFolderPath, 'css')
        #self.cssFilePath = os.path.join(self.cssFolderPath, 'custom_track_styles.css')
        self.logger = logging.getLogger(__name__)

    

    def addTrack(self, trackDbObject):
        if trackDbObject['dataType'].lower() == 'bam':
            #new_track = subprocess.Popen(['echo', trackDbObject['options']], stdout=subprocess.PIPE)
            #subprocess.call(['add-track-json.pl', json_file], stdin=new_track.stdout)
            subtools.add_track_json(self.trackList, trackDbObject['options'])
            #subtools.add_track_json(self.trackList, trackDbObject['track_json'])
        elif trackDbObject['dataType'].lower() == 'bigwig':
            subtools.add_track_json(self.trackList, trackDbObject['options'])
        else: 
            if trackDbObject['trackType'] == 'HTMLFeatures':
                self._customizeHTMLFeature(trackDbObject)
            subtools.flatfile_to_json(trackDbObject['trackDataURL'], trackDbObject['dataType'], trackDbObject['trackType'], trackDbObject['trackLabel'], self.mySpecieFolderPath, trackDbObject['options'])


    def terminate(self, debug=False):
        """ Write html file """
        self._indexName()
        if not debug:
            self._removeRaw()
        self._makeArchive()
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
        #try:
            #print os.path.join(self.tool_dir, 'prepare-refseqs.pl') + ", '--fasta', " + self.reference +", '--out', self.json])"
            #subprocess.call(['prepare-refseqs.pl', '--fasta', self.reference_genome.false_path, '--out', self.mySpecieFolderPath])
        #except OSError as e:
            #print "Cannot prepare reference error({0}): {1}".format(e.errno, e.strerror)

    def _indexName(self):
        #subprocess.call(['generate-names.pl', '-v', '--out', self.mySpecieFolderPath])
        subtools.generate_names(self.mySpecieFolderPath)
        print "finished name index \n"

    def _outHtml(self, host_name):
        with open(self.outputFile, 'w') as htmlfile:
            htmlstr = 'The new Organism "%s" is created on Apollo: <br>' % self.genome_name
            jbrowse_hub = '<li><a href = "%s" target="_blank">View JBrowse Hub on Apollo</a></li>' % host_name
            htmlstr += jbrowse_hub
            htmlfile.write(htmlstr)     

    def _makeArchive(self):
        self.apollo.loadHubToApollo(self.apollo_user, self.genome_name, self.mySpecieFolderPath, admin=True)
        apollo_host = self.apollo.getHost()
        self._outHtml(apollo_host)
        

    def __createAssemblyHub__(self, extra_files_path):
        # Get all necessaries infos first
        # 2bit file creation from input fasta

        # baseNameFasta = os.path.basename(fasta_file_name)
        # suffixTwoBit, extensionTwoBit = os.path.splitext(baseNameFasta)
        # nameTwoBit = suffixTwoBit + '.2bit'
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

        # TODO: Manage to put every fill Function in a file dedicated for reading reasons
        # Create the root directory
        myHubPath = os.path.join(extra_files_path, "myHub")
        if not os.path.exists(myHubPath):
            os.makedirs(myHubPath)

        # Create the specie folder
        # TODO: Generate the name depending on the specie
        mySpecieFolderPath = os.path.join(myHubPath, self.genome_name)
        if not os.path.exists(mySpecieFolderPath):
            os.makedirs(mySpecieFolderPath)
        self.mySpecieFolderPath = mySpecieFolderPath

        # We create the 2bit file while we just created the specie folder
        #self.twoBitName = self.genome_name + ".2bit"
        #self.two_bit_final_path = os.path.join(self.mySpecieFolderPath, self.twoBitName)
        #shutil.copyfile(twoBitFile.name, self.two_bit_final_path)

        # Create the folder tracks into the specie folder
        tracksFolderPath = os.path.join(mySpecieFolderPath, "raw")
        if not os.path.exists(tracksFolderPath):
            os.makedirs(tracksFolderPath)
        self.myTracksFolderPath = tracksFolderPath

        myBinaryFolderPath = os.path.join(mySpecieFolderPath, 'bbi')
        if not os.path.exists(myBinaryFolderPath):
            os.makedirs(myBinaryFolderPath)
        self.myBinaryFolderPath = myBinaryFolderPath

        return myHubPath
