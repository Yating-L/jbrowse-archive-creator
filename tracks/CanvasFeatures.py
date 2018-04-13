#!/usr/bin/env python
import os
import json
import logging

from TrackDb import TrackDb
from util import subtools


class CanvasFeatures(TrackDb):
    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        super(CanvasFeatures, self).__init__(trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings)

    def prepareExtraSetting(self):
        if 'category' not in self.extraSettings or not self.extraSettings['category']:
            self.extraSettings['category'] = "Default group"
        self.extraSettings['style'] = {}
        self.extraSettings['style']['className'] = 'feature'
        if 'color' not in self.extraSettings or not self.extraSettings['color']:
            self.extraSettings['style']['color'] = "#FFA600"
        else:
            self.extraSettings['style']['color'] = self.extraSettings['color']
        track = dict()
        track['type'] = 'JBrowse/View/Track/' + self.trackType
        track['storeClass'] = 'JBrowse/Store/SeqFeature/GFF3Tabix'
        if self.dataType == 'gff':
            track['urlTemplate'] = os.path.join('tracks', self.trackName + '.gff3.gz')
        else:
            track['urlTemplate'] = os.path.join('tracks', self.trackName)
        track['label'] = self.trackLabel
        track['category'] = self.extraSettings['category']
        track['style'] = self.extraSettings['style']
        extraConfigs = track
        return extraConfigs

