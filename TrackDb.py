#!/usr/bin/python
import os
import collections
import json
import logging
from util import santitizer

class TrackDb(object):
    """docstring for TrackDb"""
    

    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        #super(TrackDb, self).__init__()
        not_init_message = "The {0} is not initialized." 
        if trackName is None:
            raise TypeError(not_init_message.format('trackName'))
        if trackLabel is None:
            raise TypeError(not_init_message.format('trackLabel'))
        if trackType is None:
            raise TypeError(not_init_message.format('trackType'))
        self.trackName = trackName
        self.trackLabel = trackLabel
        self.trackDataURL = trackDataURL
        self.trackType = trackType
        self.dataType = dataType
        self.extraSettings = extraSettings
        self.logger = logging.getLogger(__name__)
        self.createTrackDb()

    def createTrackDb(self):
    
        # TODO: Remove the hardcoded "tracks" by the value used as variable from myTrackFolderPath
        #data_url = "tracks/%s" % self.trackName
        #track_label = self.trackLabel.replace("_", " ")
        #data_url = "tracks/%s" % self.trackLabel
        #sanitize the track_name
        #sanitized_name = santitizer.prefixTrackName(track_name)

        self.track_db = collections.OrderedDict([("track",self.trackName),
                ("trackLabel",self.trackLabel),
                ("trackDataURL",self.trackDataURL),
                ("dataType", self.dataType),
                ("trackType", self.trackType)]
                )
        
        
        extraConfigs = self.prepareExtraSetting()
        self.logger.debug("Generate extraConfigs = %s", json.dumps(extraConfigs))
        self.track_db["options"] = extraConfigs
        #print self.track_db
        self.logger.debug("TrackDb object is created track_db = %s ", json.dumps(self.track_db))
    
    def prepareExtraSetting(self):
        
        if self.trackType == "CanvasFeatures":
            return self.configCanvasFeatures()
        elif self.trackType == "HTMLFeatures":
            return self.configHTMLFeatures()
        elif self.trackType == "bam":
            return self.configBam()
        elif self.trackType == "bigwig":
            return self.configBigWig()
        else:
            #return self.configCanvasFeatures()
            raise ValueError("%s is not valid", self.trackType)
        
        
        '''
        if self.dataType == 'blastxml':
            self.extraSettings['type'] = "G-OnRamp_plugin/BlastAlignment"
        elif self.dataType == 'bigpsl':
            self.extraSettings['type'] = "G-OnRamp_plugin/BlatAlignment"
        elif self.dataType == 'gff3_transcript' or self.dataType == 'gff3_mrna':
            self.extraSettings['type'] = "G-OnRamp_plugin/GenePred"
        else:
            self.extraSettings['type'] = "CanvasFeatures"
        '''
    def configHTMLFeatures(self):
        """ set HTMLFeatures configuration options """
        extraConfigs = dict()
        self.extraSettings["clientConfig"] = dict()
        self.extraSettings["config"] = dict()
        if 'type' in self.extraSettings:
            extraConfigs["type"] = self.extraSettings['type']
        if 'color' in self.extraSettings and self.extraSettings['color']:
            extraConfigs['feature_color'] = self.extraSettings['color']
        else:
            extraConfigs['feature_color'] = "#000000"
        #self.extraSettings['clientConfig']['color'] = self.extraSettings['color']
        if 'subfeatureClasses' in self.extraSettings:
            subfeature_css_class = santitizer.sanitize_name(self.trackLabel + "_" + self.extraSettings['subfeatureClasses'])
            extraConfigs['subfeatureClasses'] = {self.extraSettings['subfeatureClasses']: subfeature_css_class}

        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings['config']['category'] = "Default group"
        else:
            self.extraSettings['config']['category'] = self.extraSettings['category']
    
        extraConfigs['config'] = json.dumps(self.extraSettings["config"])
        extraConfigs['clientConfig'] = json.dumps(self.extraSettings["clientConfig"])
        return extraConfigs
    
    def configBam(self):
        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings['category'] = "Default group"
        bam_track = dict()
        bam_track['type'] = 'JBrowse/View/Track/Alignments2'
        bam_track['storeClass'] = 'JBrowse/Store/SeqFeature/BAM'
        bam_track['urlTemplate'] = os.path.join('bbi', self.trackName)
        bam_track['baiUrlTemplate'] = os.path.join('bbi', self.extraSettings['index'])
        bam_track['label'] = self.trackLabel
        bam_track['category'] = self.extraSettings['category']
        #extraConfigs = json.dumps(bam_track)
        extraConfigs = bam_track
        return extraConfigs

    def configBigWig(self):
        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings['category'] = "Default group"
        if 'style' not in self.extraSettings:
            self.extraSettings['style'] = {}
            if 'pos_color' not in self.extraSettings['style'] or self.extraSettings['style']['pos_color'] == '':
                self.extraSettings['style']['pos_color'] = "#FFA600"
            if 'neg_color' not in self.extraSettings['style'] or self.extraSettings['style']['neg_color'] == '':
                self.extraSettings['style']['neg_color'] = "#005EFF"
        bigwig_track = dict()
        bigwig_track['urlTemplate'] = os.path.join('bbi', self.trackName)
        bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
        bigwig_track['storeClass'] = 'JBrowse/Store/SeqFeature/BigWig'
        bigwig_track['label'] = self.trackLabel
        bigwig_track['style'] = self.extraSettings['style']
        bigwig_track['category'] = self.extraSettings['category']
        #extraConfigs = json.dumps(bigwig_track)
        extraConfigs = bigwig_track
        return extraConfigs

    def configCanvasFeatures(self):
        """ set CanvasFeatures configuration options """
        extraConfigs = dict()
        self.extraSettings["clientConfig"] = dict()
        self.extraSettings["config"] = dict()
        if 'color' not in self.extraSettings or not self.extraSettings['color']:
            self.extraSettings["clientConfig"]['color'] = "#daa520"
        else:
            self.extraSettings["clientConfig"]['color'] = self.extraSettings['color']
        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings["config"]['category'] = "Default group"
        else:
            self.extraSettings["config"]['category'] = self.extraSettings['category']
        if 'glyph' in self.extraSettings:
            self.extraSettings["config"]['glyph'] = self.extraSettings['glyph']
        if 'transcriptType' in self.extraSettings:
            self.extraSettings['Config']['transcriptType'] = self.extraSettings['transcriptType']
        extraConfigs["config"] = json.dumps(self.extraSettings["config"])
        extraConfigs["clientConfig"] = json.dumps(self.extraSettings["clientConfig"])
        return extraConfigs

        
    
    def get(self, item_name):
        if item_name in self.track_db:
            return self.track_db[item_name]
        return None

    