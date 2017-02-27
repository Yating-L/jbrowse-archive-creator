#!/usr/bin/env python

import os
import trackObject
import utils
import subprocess
import string
import shutil

class TrackHub:
    def __init__(self, inputFiles, reference, outputDirect, tool_dir):
        self.input_files = inputFiles
        self.out_path = outputDirect
        self.reference = reference
        self.tool_dir = tool_dir
        try: 
            if not self.out_path:
                raise ValueError('empty output path\n')
            if os.path.exists(self.out_path):
                shutil.rmtree(self.out_path)
            os.mkdir(self.out_path)
            self.json = os.path.join(self.out_path, 'json')
            if os.path.exists(self.json):
                shutil.rmtree(self.json)
            os.mkdir(self.json)
            self.raw = os.path.join(self.out_path, 'raw')
            if os.path.exists(self.raw):
                shutil.rmtree(self.raw)
            shutil.move('raw', self.out_path)
        except OSError as e:
            print "Cannot create json folder error({0}): {1}".format(e.errno, e.strerror)
        else:
            print "Create jbrowse folder {}".format(self.out_path)
    
    def createHub(self):
        self.prepareRefseq()
        for input_file in self.input_files:
            self.addTrack(input_file)
        self.indexName()
        print "Success!\n"
    
    def prepareRefseq(self):
        try:
            p = subprocess.Popen([os.path.join(self.tool_dir, 'prepare-refseqs.pl'), '--fasta', self.reference, '--out', self.json])
            # Wait for process to terminate.
            p.communicate()
        except OSError as e:
            print "Cannot prepare reference error({0}): {1}".format(e.errno, e.strerror)

    def addTrack(self, trackObject = None):
        if trackObject.dataType == 'bam':
            json_file = os.path.join(self.json, "trackList.json")
            bam_track = dict()
            bam_track['type'] = 'JBrowse/View/Track/Alignments2'
            bam_track['label'] = 'alignments'
            bam_track['urlTemplate'] = os.path.join('../raw', trackObject.fileName)
            utils.add_tracks_to_json(json_file, bam_track, 'add_tracks')
            print "add bam track\n"
        elif trackObject.dataType == 'bigwig':
            json_file = os.path.join(self.json, "trackList.json")
            bigwig_track = dict()
            bigwig_track['label'] = 'rnaseq'
            bigwig_track['key'] = 'RNA-Seq Coverage'
            bigwig_track['urlTemplate'] = os.path.join('../raw', trackObject.fileName)
            bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
            bigwig_track['variance_band'] = True
            bigwig_track['style'] = dict()
            bigwig_track['style']['pos_color'] = '#FFA600'
            bigwig_track['style']['neg_color'] = '#005EFF'
            bigwig_track['style']['clip_marker_color'] = 'red'
            bigwig_track['style']['height'] = 100
            utils.add_tracks_to_json(json_file, bigwig_track, 'add_tracks')
        else: 
            gff3_file = os.path.join(self.raw, trackObject.fileName)
            label = trackObject.fileName
            if trackObject.dataType == 'bedSpliceJunctions':
                p = subprocess.Popen([os.path.join(self.tool_dir, 'flatfile-to-json.pl'), '--gff', gff3_file, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--config', '{"glyph": "JBrowse/View/FeatureGlyph/Segments"}', '--out', self.json])
            else:
                p = subprocess.Popen([os.path.join(self.tool_dir, 'flatfile-to-json.pl'), '--gff', gff3_file, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', self.json])
            p.communicate()
            
            '''
            if trackObject.dataType == 'gff3':
                attr = dict()
                track = dict()
                attr['transcriptType'] = 'transcript'
                track['Augustus'] = attr
                json_file = os.path.join(self.json, "trackList.json")
                utils.add_tracks_to_json(json_file, track, 'add_attr')
            elif trackObject.dataType == 'bedSpliceJunctions':
                attr = dict()
                track = dict()
                attr['glyph'] = 'JBrowse/View/FeatureGlyph/Segments'
                track['regtools'] = attr
                json_file = os.path.join(self.json, "trackList.json")
                utils.add_tracks_to_json(json_file, track, 'add_attr')
                '''
    def indexName(self):
        p = subprocess.Popen([os.path.join(self.tool_dir, 'generate-names.pl'), '-v', '--out', self.json])
        p.communicate()
        print "finished name index \n"

