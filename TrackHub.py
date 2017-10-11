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
from util import subtools
from util import santitizer


class TrackHub:
    def __init__(self, inputFastaFile, user_email, outputFile, extra_files_path, tool_directory, trackType=None, apollo_host=None):
        
        self.rootAssemblyHub = None

        self.mySpecieFolderPath = None
        # Store intermediate files, will be removed if not in debug mode
        self.myTracksFolderPath = None
        # Store binary files: Bam, BigWig
        self.myBinaryFolderPath = None
        self.tool_directory = tool_directory
        self.trackType = trackType

        self.reference_genome = inputFastaFile
        # TODO: Add the specie name
        self.genome_name = inputFastaFile.assembly_id
        self.specie_html = self.genome_name + '.html'
        self.default_pos = None
        self.user_email = user_email
        self.extra_files_path = extra_files_path
        self.outputFile = outputFile

        # Template groups
        mylookup = TemplateLookup(directories=[os.path.join(self.tool_directory, 'templates')],
                                  output_encoding='utf-8', encoding_errors='replace')
        self.cssTemplate = mylookup.get_template("custom_track_styles.css")
        

        # Create the structure of the Assembly Hub
        # TODO: Merge the following processing into a function as it is also used in twoBitCreator
        self.twoBitName = None
        self.two_bit_final_path = None
        self.chromSizesFile = None

        # Set all the missing variables of this class, and create physically the folders/files
        self.rootAssemblyHub = self.__createAssemblyHub__(extra_files_path=extra_files_path)
        # Init the Datatype
        Datatype.pre_init(self.reference_genome, self.two_bit_final_path, self.chromSizesFile,
                          self.extra_files_path, self.tool_directory,
                          self.mySpecieFolderPath, self.myTracksFolderPath, self.myBinaryFolderPath, self.trackType)  

        self.prepareRefseq()
        self.trackList = os.path.join(self.mySpecieFolderPath, "trackList.json")
        self.createTrackList()
        self.apollo_host = apollo_host
        self.cssFolderPath = os.path.join(self.mySpecieFolderPath, 'css')
        self.cssFilePath = os.path.join(self.cssFolderPath, 'custom_track_styles.css')
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
            self.customizeFeatures(trackDbObject)
            subtools.flatfile_to_json(trackDbObject['trackDataURL'], trackDbObject['dataType'], trackDbObject['trackType'], trackDbObject['trackLabel'], self.mySpecieFolderPath, trackDbObject['options'])
            '''
            if track['dataType'] == 'bed':
                subprocess.call(['flatfile-to-json.pl', '--bed', flat_file, '--trackType', track['type'], '--trackLabel', track['label'], '--Config', '{"category" : "%s"}' % track['category'], '--clientConfig', '{"color" : "%s"}' % track['color'], '--out', self.mySpecieFolderPath])
            elif track['dataType'] == 'bedSpliceJunctions' or track['dataType'] == 'gtf' or track['dataType'] == 'blastxml':
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', track['type'], '--trackLabel', track['label'], '--Config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments", "category" : "%s"}' % track['category'], '--clientConfig', '{"color" : "%s"}' % track['color'], '--out', self.mySpecieFolderPath])
            elif track['dataType'] == 'gff3_transcript':
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', track['type'], '--trackLabel', track['label'], '--Config', '{"transcriptType": "transcript", "category" : "%s"}' % track['category'], '--clientConfig', '{"color" : "%s"}' % track['color'], '--out', self.mySpecieFolderPath])
            else:
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', track['type'], '--trackLabel', track['label'], '--Config', '{"category" : "%s"}' % track['category'], '--clientConfig', '{"color" : "%s"}' % track['color'], '--out', self.mySpecieFolderPath])
            '''
        
        


    def customizeFeatures(self, trackDbObject):
        if trackDbObject['options']:
            subfeatures = trackDbObject['options'].get('subfeatureClasses')
            feature_color = trackDbObject['options']['feature_color']
            if subfeatures:
                for key, value in subfeatures.items():
                    self.createCssClass(value, feature_color)
            else:
                customizedFeature = santitizer.sanitize_name(trackDbObject['trackLabel'])
                clientConfig = json.loads(trackDbObject['options']['clientConfig'])
                clientConfig['renderClassName'] = customizedFeature
                trackDbObject['options']['clientConfig'] = json.dumps(clientConfig)
                self.createCssClass(customizedFeature, feature_color)
            self.addCustimizedCss()

    def createCssClass(self, feature_css_name, feature_color):
        if not os.path.exists(self.cssFilePath):
            if not os.path.exists(self.cssFolderPath):
                os.mkdir(self.cssFolderPath)
            os.mknod(self.cssFilePath)   
        with open(self.cssFilePath, 'a+') as css:
            htmlMakoRendered = self.cssTemplate.render(
            label = feature_css_name,
            color = feature_color
        )
            css.write(htmlMakoRendered)
        self.logger.debug("create customized track css class: cssFilePath= %s", self.cssFilePath)

    def addCustimizedCss(self):
        with open(self.trackList, 'r+') as track:
            data = json.load(track)
            css_path = os.path.join('data', 'css', 'custom_track_styles.css')
            data['css'] = {'url': css_path}
            json_string = json.dumps(data, indent=4, separators=(',', ': '))
            track.seek(0)
            track.write(json_string)
            track.truncate()
        self.logger.debug("added customized css url to trackList.json")
    

    def terminate(self, debug=False):
        """ Write html file """
        self.indexName()
        if not debug:
            self.removeRaw()
        self.makeArchive()
        #self.outHtml(slink)
        #slink = self.linkCustomCss()
        print "Success!\n"

    def removeRaw(self):
        if os.path.exists(self.myTracksFolderPath):
            shutil.rmtree(self.myTracksFolderPath)

    def createTrackList(self):
        if not os.path.exists(self.trackList):
            os.mknod(self.trackList)   

    def prepareRefseq(self):
        try:
            #print os.path.join(self.tool_dir, 'prepare-refseqs.pl') + ", '--fasta', " + self.reference +", '--out', self.json])"
            subprocess.call(['prepare-refseqs.pl', '--fasta', self.reference_genome.false_path, '--out', self.mySpecieFolderPath])
        except OSError as e:
            print "Cannot prepare reference error({0}): {1}".format(e.errno, e.strerror)

    def indexName(self):
        subprocess.call(['generate-names.pl', '-v', '--out', self.mySpecieFolderPath])
        print "finished name index \n"

    
    '''
    def _addCssToTrackList(self):
        with open(self.trackList, 'r+') as track:
            data = json.load(track)
            data['css'] = {'url': 'custom_track_styles.css'}
            json_string = json.dumps(data, indent=4, separators=(',', ': '))
            track.seek(0)
            track.write(json_string)
            track.truncate()
        self.logger.debug("added customized css url to trackList.json")
    '''
    def addOrganism(self):
        subtools.arrow_add_organism(self.genome_name, self.mySpecieFolderPath)


    def outHtml(self):
        with open(self.outputFile, 'w') as htmlfile:
            htmlstr = 'The new Organism "%s" is created on Apollo: <br>' % self.genome_name
            jbrowse_hub = '<li><a href = "%s" target="_blank">View JBrowse Hub on Apollo</a></li>' % self.apollo_host
            htmlstr += jbrowse_hub
            htmlfile.write(htmlstr)     

    def makeArchive(self):
        #self.addCustimizedCss()
        self.addOrganism()
        self.outHtml()
        
        

    '''
    def makeArchive(self):
        file_dir = os.path.abspath(self.outputFile)
        source_dir = os.path.dirname(file_dir)
        folder_name = os.path.basename(self.extra_files_path)
        source_name = os.path.basename(self.mySpecieFolderPath)
        source = os.path.join(source_dir, folder_name, source_name)
        slink = source.replace('/', '_')
        slink = os.path.join('/var/www/html/JBrowse-1.12.1/data', slink)
        try:
            if os.path.islink(slink):
                os.unlink(slink)
        except OSError as oserror:
            print "Cannot create symlink to the data({0}): {1}".format(oserror.errno, oserror.strerror)
        os.symlink(source, slink)
        return slink
    
    def outHtml(self, slink):
        with open(self.outputFile, 'w') as htmlfile:
            htmlstr = 'The JBrowse Hub is created: <br>'
            url = self.jbrowse_host + "/JBrowse-1.12.1/index.html?data=%s"
            jbrowse_hub = '<li><a href = "%s" target="_blank">View JBrowse Hub</a></li>' % url
            link_name = os.path.basename(slink)
            relative_path = os.path.join('data', link_name + '/json')
            htmlstr += jbrowse_hub % relative_path
            htmlfile.write(htmlstr)                                                      
    '''

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
        self.twoBitName = self.genome_name + ".2bit"
        self.two_bit_final_path = os.path.join(self.mySpecieFolderPath, self.twoBitName)
        shutil.copyfile(twoBitFile.name, self.two_bit_final_path)

      

        # Create the file groups.txt
        # TODO: If not inputs for this, do no create the file
        # groupsTxtFilePath = os.path.join(mySpecieFolderPath, 'groups.txt')
        # self.__fillGroupsTxtFile__(groupsTxtFilePath)

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
'''
        #self.input_files = inputFiles.tracks
        self.outputFile = outputFile
        self.outfolder = extra_files_path
        self.out_path = os.path.join(extra_files_path, 'myHub')
        self.reference = reference
        self.tool_dir = tool_dir
        self.metaData = metaData
        self.raw = os.path.join(self.out_path, 'raw')
        self.json = os.path.join(self.out_path, 'json')
        self.jbrowse_host = "localhost"
        try: 
            if os.path.exists(self.json):
                shutil.rmtree(self.json)
            os.makedirs(self.json)
        except OSError as e:
            print "Cannot create json folder error({0}): {1}".format(e.errno, e.strerror)
        else:
            print "Create jbrowse folder {}".format(self.out_path)
    
    def createHub(self):
        self.prepareRefseq()
        for input_file in self.input_files:
            self.addTrack(input_file)
        self.indexName()
        slink = self.makeArchive()
        self.outHtml(slink)
        print "Success!\n"
    
    def prepareRefseq(self):
        try:
            #print os.path.join(self.tool_dir, 'prepare-refseqs.pl') + ", '--fasta', " + self.reference +", '--out', self.json])"
            subprocess.call(['prepare-refseqs.pl', '--fasta', self.reference, '--out', self.json])
        except OSError as e:
            print "Cannot prepare reference error({0}): {1}".format(e.errno, e.strerror)
    #TODO: hard coded the bam and bigwig tracks. Need to allow users to customize the settings
    def addTrack(self, track):
        #print "false_path" , track['false_path']
        if track['false_path'] in self.metaData.keys():
            metadata = self.metaData[track['false_path']]
        else:
            metadata = {}
        self.SetMetadata(track, metadata)
        if track['dataType'] == 'bam':
            self.Bam(track, metadata)
           # print "add bam track\n"
        elif track['dataType'] == 'bigwig':
            self.BigWig(track, metadata)
        else: 
            flat_file = os.path.join(self.raw, track['fileName'])
            if track['dataType'] == 'bed':
                subprocess.call(['flatfile-to-json.pl', '--bed', flat_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            elif track['dataType'] == 'bedSpliceJunctions' or track['dataType'] == 'gtf' or track['dataType'] == 'blastxml':
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            elif track['dataType'] == 'gff3_transcript':
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"transcriptType": "transcript", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            else:
                subprocess.call(['flatfile-to-json.pl', '--gff', flat_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            
    def indexName(self):
        subprocess.call(['generate-names.pl', '-v', '--out', self.json])
        print "finished name index \n"

    def makeArchive(self):
        file_dir = os.path.abspath(self.outfile)
        source_dir = os.path.dirname(file_dir)
        folder_name = os.path.basename(self.outfolder)
        source_name = os.path.basename(self.out_path)
        source = os.path.join(source_dir, folder_name, source_name)
        slink = source.replace('/', '_')
        slink = os.path.join('/var/www/html/JBrowse-1.12.1/data', slink)
        try:
            if os.path.islink(slink):
                os.unlink(slink)
        except OSError as oserror:
            print "Cannot create symlink to the data({0}): {1}".format(oserror.errno, oserror.strerror)
        os.symlink(source, slink)
        return slink
    
    def outHtml(self, slink):
        with open(self.outfile, 'w') as htmlfile:
            htmlstr = 'The JBrowse Hub is created: <br>'
            url = self.jbrowse_host + "/JBrowse-1.12.1/index.html?data=%s"
            jbrowse_hub = '<li><a href = "%s" target="_blank">View JBrowse Hub</a></li>' % url
            link_name = os.path.basename(slink)
            relative_path = os.path.join('data', link_name + '/json')
            htmlstr += jbrowse_hub % relative_path
            htmlfile.write(htmlstr)

    def createTrackList(self):
        trackList = os.path.join(self.json, "trackList.json")
        if not os.path.exists(trackList):
            os.mknod(trackList)
    
    def Bam(self, track, metadata):
        #create trackList.json if not exist
        self.createTrackList()
        json_file = os.path.join(self.json, "trackList.json")
        bam_track = dict()
        bam_track['type'] = 'JBrowse/View/Track/Alignments2'
        bam_track['storeClass'] = 'JBrowse/Store/SeqFeature/BAM'
        bam_track['urlTemplate'] = os.path.join('../raw', track['fileName'])
        bam_track['baiUrlTemplate'] = os.path.join('../raw', track['index'])
        bam_track['label'] = metadata['label']
        bam_track['category'] = metadata['category']
        bam_track = json.dumps(bam_track)
        #Use add-track-json.pl to add bam track to json file
        new_track = subprocess.Popen(['echo', bam_track], stdout=subprocess.PIPE)
        subprocess.call(['add-track-json.pl', json_file], stdin=new_track.stdout)
    
    def BigWig(self, track, metadata):
        #create trackList.json if not exist
        self.createTrackList()
        json_file = os.path.join(self.json, "trackList.json")
        bigwig_track = dict()
        bigwig_track['urlTemplate'] = os.path.join('../raw', track['fileName'])
        bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
        bigwig_track['storeClass'] = 'JBrowse/Store/SeqFeature/BigWig'
        bigwig_track['label'] = metadata['label']
        bigwig_track['style'] = metadata['style']
        bigwig_track['category'] = metadata['category']
        bigwig_track = json.dumps(bigwig_track)
        #Use add-track-json.pl to add bigwig track to json file
        new_track = subprocess.Popen(['echo', bigwig_track], stdout=subprocess.PIPE)
        #output = new_track.communicate()[0]
        subprocess.call(['add-track-json.pl', json_file], stdin=new_track.stdout)

    #If the metadata is not set, use the default value
    def SetMetadata(self, track, metadata):
        if 'label' not in metadata.keys() or metadata['label'] == '':
            metadata['label'] = track['fileName']
        if 'color' not in metadata.keys() or metadata['color'] == '':
            metadata['color'] = "#daa520"
        if track['dataType'] == 'bigwig':
            if 'style' not in metadata.keys():
                metadata['style'] = {}
            if 'pos_color' not in metadata['style'] or metadata['style']['pos_color'] == '':
                metadata['style']['pos_color'] = "#FFA600"
            if 'neg_color' not in metadata['style'] or metadata['style']['neg_color'] == '':
                metadata['style']['neg_color'] = "#005EFF"
        if 'category' not in metadata.keys() or metadata['category'] == '':
            metadata['category'] = "Default group"
        if track['dataType'] == 'blastxml':
            metadata['type'] = "G-OnRamp_plugin/BlastAlignment"
        elif track['dataType'] == 'bigpsl':
            metadata['type'] = "G-OnRamp_plugin/BlatAlignment"
        elif track['dataType'] == 'gff3_transcript' or track['dataType'] == 'gff3_mrna':
            metadata['type'] = "G-OnRamp_plugin/GenePred"
        else:
            metadata['type'] = "CanvasFeatures"

'''

   



