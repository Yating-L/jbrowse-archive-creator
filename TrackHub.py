#!/usr/bin/env python

import os
import subprocess
import shutil
import utils


class TrackHub:
    def __init__(self, inputFiles, reference, outputDirect, tool_dir, genome, extra_files_path, metaData):
        self.input_files = inputFiles.tracks
        self.outfile = outputDirect
        self.outfolder = extra_files_path
        self.out_path = os.path.join(extra_files_path, genome)
        self.reference = reference
        self.tool_dir = tool_dir
        self.metaData = metaData
        self.raw = os.path.join(self.out_path, 'raw')
        self.json = os.path.join(self.out_path, 'json')
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
        self.makeArchive()
        self.outHtml()
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
            gff3_file = os.path.join(self.raw, track['fileName'])
            if track['dataType'] == 'bedSpliceJunctions' or track['dataType'] == 'gtf' or track['dataType'] == 'blastxml':
                subprocess.call(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            elif track['dataType'] == 'gff3_transcript':
                subprocess.call(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"transcriptType": "transcript", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            else:
                subprocess.call(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            
    def indexName(self):
        subprocess.call(['generate-names.pl', '-v', '--out', self.json])
        print "finished name index \n"

    def makeArchive(self):
        shutil.make_archive(self.out_path, 'zip', self.out_path)
        data_folder = '/var/www/html/JBrowse-1.12.1/jbrowse_hub'
        try:
            if os.path.exists(data_folder):
                if os.path.isdir(data_folder):
                    shutil.rmtree(data_folder)
                else:
                    os.remove(data_folder)
        except OSError as oserror:
            print "Cannot create data folder({0}): {1}".format(oserror.errno, oserror.strerror)
        shutil.copytree(self.out_path, data_folder)
        subprocess.call(['chmod', '-R', 'o+rx', '/var/www/html/JBrowse-1.12.1/jbrowse_hub'])
        shutil.rmtree(self.out_path)
    
    #TODO: this will list all zip files in the filedir and sub-dirs. worked in Galaxy but all list zip files in test-data when
    #run it locally. May need modify
    def outHtml(self):
        with open(self.outfile, 'w') as htmlfile:
            htmlstr = 'The JBrowse Hub is created: <br>'
            zipfiles = '<li><a href = "%s">Download</a></li>'
            jbrowse_hub = '<li><a href = "http://192.168.56.11/JBrowse-1.12.1/index.html?data=jbrowse_hub/json" target="_blank">View JBrowse Hub</a></li>'
            filedir_abs = os.path.abspath(self.outfile)
            filedir = os.path.dirname(filedir_abs)
            filedir = os.path.join(filedir, self.outfolder)
            for root, dirs, files in os.walk(filedir):
                for file in files:
                    if file.endswith('.zip'):   
                        relative_directory = os.path.relpath(root, filedir)
                        relative_file_path = os.path.join(relative_directory, file)
                        htmlstr += zipfiles % relative_file_path
            htmlstr += jbrowse_hub
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
        utils.add_tracks_to_json(json_file, bam_track, 'add_tracks')

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
        utils.add_tracks_to_json(json_file, bigwig_track, 'add_tracks')

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
                metadata['pos_color'] = "#FFA600"
            if 'neg_color' not in metadata['style'] or metadata['style']['neg_color'] == '':
                metadata['neg_color'] = "#005EFF"
        if 'category' not in metadata.keys() or metadata['category'] == '':
            metadata['category'] = "Default group"
        if track['dataType'] == 'blastxml':
            metadata['type'] = "G-OnRamp_plugin/BlastAlignment"
        elif track['dataType'] == 'gff3_transcript' or track['dataType'] == 'gff3_mrna':
            metadata['type'] = "G-OnRamp_plugin/GenePred"
        else:
            metadata['type'] = "CanvasFeatures"



   



