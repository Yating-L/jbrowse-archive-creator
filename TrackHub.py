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
            p = subprocess.Popen(['prepare-refseqs.pl', '--fasta', self.reference, '--out', self.json])
            # Wait for process to terminate.
            p.communicate()
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
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            elif track['dataType'] == 'gff3_transcript':
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"transcriptType": "transcript", "category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            else:
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', metadata['type'], '--trackLabel', metadata['label'], '--Config', '{"category" : "%s"}' % metadata['category'], '--clientConfig', '{"color" : "%s"}' % metadata['color'], '--out', self.json])
            p.communicate()
            
    def indexName(self):
        p = subprocess.Popen(['generate-names.pl', '-v', '--out', self.json])
        p.communicate()
        print "finished name index \n"

    def makeArchive(self):
        shutil.make_archive(self.out_path, 'zip', self.out_path)  
        shutil.rmtree(self.out_path) 
    
    #TODO: this will list all zip files in the filedir and sub-dirs. worked in Galaxy but all list zip files in test-data when
    #run it locally. May need modify
    def outHtml(self):
        with open(self.outfile, 'w') as htmlfile:
            htmlstr = 'The JBrowse Hub is created: <br>'
            zipfiles = '<li><a href = "%s">Download</a></li>'
            filedir_abs = os.path.abspath(self.outfile)
            filedir = os.path.dirname(filedir_abs)
            filedir = os.path.join(filedir, self.outfolder)
            for root, dirs, files in os.walk(filedir):
                for file in files:
                    if file.endswith('.zip'):   
                        relative_directory = os.path.relpath(root, filedir)
                        relative_file_path = os.path.join(relative_directory, file)
                        htmlstr += zipfiles % relative_file_path
                        
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
        #color_setting = {"pos_color" : track['pos_color'], "neg_color" : track['neg_color']} 
        #bigwig_track['style'] = {"pos_color" : track['pos_color'], "neg_color" : track['neg_color']} 
        bigwig_track['urlTemplate'] = os.path.join('../raw', track['fileName'])
        bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
        bigwig_track['storeClass'] = 'JBrowse/Store/SeqFeature/BigWig'
        bigwig_track['label'] = metadata['label']
        bigwig_track['style'] = metadata['style']
        bigwig_track['category'] = metadata['category']
        utils.add_tracks_to_json(json_file, bigwig_track, 'add_tracks')

    #If the metadata is not set, use the default value
    def SetMetadata(self, track, metadata):
        #print metadata
        #track.update(metadata)
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



   



