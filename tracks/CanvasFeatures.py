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
            # need .gff3.gz extension to index the name of the track with generate-name.pl
            track['urlTemplate'] = os.path.join('tracks', self.trackName + '.gff3.gz')
            # needed to show match_part in Blat and Blast alignment as subfeatures
            track['glyph'] = "JBrowse/View/FeatureGlyph/Segments"
        else:
            track['urlTemplate'] = os.path.join('tracks', self.trackName)
        if 'subfeatureClasses' in self.extraSettings:
            track['subfeatureClasses'] = self.extraSettings['subfeatureClasses']
        track['label'] = self.trackLabel
        track['category'] = self.extraSettings['category']
        track['style'] = self.extraSettings['style']
        extraConfigs = track
        return extraConfigs

