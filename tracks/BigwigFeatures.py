#!/usr/bin/env python
import os
import json
import logging

from TrackDb import TrackDb
from util import subtools
from util import santitizer


class BigwigFeatures(TrackDb):
    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        super(BigwigFeatures, self).__init__(trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings)
 
    def prepareExtraSetting(self):
        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings['category'] = "Default group"
        if 'color' not in self.extraSettings or not self.extraSettings['color']:
            self.extraSettings['style'] = {}
            self.extraSettings['style']['pos_color'] = "#FFA600"
        else:
            self.extraSettings['style'] = {}
            self.extraSettings['style']['pos_color'] = self.extraSettings['color']
            
            
        '''
        if 'style' not in self.extraSettings:
            self.extraSettings['style'] = {}
            if 'pos_color' not in self.extraSettings['style'] or self.extraSettings['style']['pos_color'] == '':
                self.extraSettings['style']['pos_color'] = "#FFA600"
            if 'neg_color' not in self.extraSettings['style'] or self.extraSettings['style']['neg_color'] == '':
                self.extraSettings['style']['neg_color'] = "#005EFF"
        '''
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

    