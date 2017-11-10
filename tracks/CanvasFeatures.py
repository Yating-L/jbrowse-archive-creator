#!/usr/bin/env python
import json
import logging

from TrackDb import TrackDb
from util import subtools


class CanvasFeatures(TrackDb):
    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        super(CanvasFeatures, self).__init__(trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings)

    def prepareExtraSetting(self):
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
            self.extraSettings['config']['transcriptType'] = self.extraSettings['transcriptType']
        extraConfigs["config"] = json.dumps(self.extraSettings["config"])
        extraConfigs["clientConfig"] = json.dumps(self.extraSettings["clientConfig"])
        return extraConfigs