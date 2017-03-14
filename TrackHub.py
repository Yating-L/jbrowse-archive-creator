#!/usr/bin/env python

import os
import trackObject
import utils
import subprocess
import string
import shutil
import tempfile

#TODO: package JBrowse file conversion .pl files

class TrackHub:
    def __init__(self, inputFiles, reference, outputDirect, tool_dir, genome, extra_files_path):
        self.input_files = inputFiles.tracks
        self.outfile = outputDirect
        self.outfolder = extra_files_path
        self.out_path = os.path.join(extra_files_path, genome)
        self.reference = reference
        self.tool_dir = tool_dir
        self.raw = os.path.join(self.out_path, 'raw')
        self.json = os.path.join(self.out_path, 'json')
        try: 
            if not self.out_path:
                raise ValueError('empty output path\n')
            if not os.path.exists(self.out_path):
                raise ValueError('the output folder has not been created')
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
        #shutil.rmtree(self.out_path)
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
        if track['dataType'] == 'bam':
            json_file = os.path.join(self.json, "trackList.json")
            bam_track = dict()
            bam_track['type'] = 'JBrowse/View/Track/Alignments2'
            bam_track['label'] = track['fileName']
            bam_track['urlTemplate'] = os.path.join('../raw', track['fileName'])
            utils.add_tracks_to_json(json_file, bam_track, 'add_tracks')
            print "add bam track\n"
        elif track['dataType'] == 'bigwig':
            json_file = os.path.join(self.json, "trackList.json")
            bigwig_track = dict()
            bigwig_track['label'] = 'rnaseq'
            bigwig_track['key'] = 'RNA-Seq Coverage'
            bigwig_track['urlTemplate'] = os.path.join('../raw', track['fileName'])
            bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
            bigwig_track['variance_band'] = True
            bigwig_track['style'] = dict()
            bigwig_track['style']['pos_color'] = '#FFA600'
            bigwig_track['style']['neg_color'] = '#005EFF'
            bigwig_track['style']['clip_marker_color'] = 'red'
            bigwig_track['style']['height'] = 100
            utils.add_tracks_to_json(json_file, bigwig_track, 'add_tracks')
        else: 
            gff3_file = os.path.join(self.raw, track['fileName'])
            label = track['fileName']
            if track['dataType'] == 'bedSpliceJunctions' or track['dataType'] == 'gtf':
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments"}', '--out', self.json])
            elif track['dataType'] == 'gff3_transcript':
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', 'MyPlugin/GenePred', '--trackLabel', label, '--config', '{"transcriptType": "transcript"}', '--out', self.json])
            elif track['dataType'] == 'gff3_mrna':
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', 'MyPlugin/GenePred', '--trackLabel', label, '--out', self.json])
            else:
                p = subprocess.Popen(['flatfile-to-json.pl', '--gff', gff3_file, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', self.json])
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
        #htmloutput = tempfile.NamedTemporaryFile(self.outfile, suffix = '.html', bufsize=0, delete=False)
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
                        
            #htmlstr = htmlstr % zipfile
            htmlfile.write(htmlstr)

   



