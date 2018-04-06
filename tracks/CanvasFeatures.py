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
        track['urlTemplate'] = os.path.join('tracks', self.trackName)
        track['label'] = self.trackLabel
        track['category'] = self.extraSettings['category']
        track['style'] = self.extraSettings['style']
        extraConfigs = track
        return extraConfigs

    # def prepareExtraSetting(self):
    #     """ set CanvasFeatures configuration options """
    #     extraConfigs = dict()
    #     self.extraSettings["clientConfig"] = dict()
    #     self.extraSettings["config"] = dict()
    #     if 'color' not in self.extraSettings or not self.extraSettings['color']:
    #         self.extraSettings["clientConfig"]['color'] = "#daa520"
    #     else:
    #         self.extraSettings["clientConfig"]['color'] = self.extraSettings['color']
    #     if 'category' not in self.extraSettings or not self.extraSettings['category']:
    #         self.extraSettings["config"]['category'] = "Default group"
    #     else:
    #         self.extraSettings["config"]['category'] = self.extraSettings['category']
    #     if 'glyph' in self.extraSettings:
    #         self.extraSettings["config"]['glyph'] = self.extraSettings['glyph']
    #     if 'transcriptType' in self.extraSettings:
    #         self.extraSettings['config']['transcriptType'] = self.extraSettings['transcriptType']
    #     extraConfigs["config"] = json.dumps(self.extraSettings["config"])
    #     extraConfigs["clientConfig"] = json.dumps(self.extraSettings["clientConfig"])
    #     return extraConfigs