#!/usr/bin/env python
import json
import logging

from TrackDb import TrackDb
from util import subtools
from util import santitizer


class HTMLFeatures(TrackDb):
    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        super(HTMLFeatures, self).__init__(trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings)
 
    def prepareExtraSetting(self):
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

        if "menuTemplate" in self.extraSettings:
            self.extraSettings["clientConfig"]["menuTemplate"] = [{}, self.extraSettings["menuTemplate"]]
            #self.extraSettings["clentConfig"]["menuTemplate"] += [{"label" : "View details"}, {"label" : "Highlight this gene"}, self.extraSettings["menuTemplate"]]

        extraConfigs['config'] = json.dumps(self.extraSettings["config"])
        extraConfigs['clientConfig'] = json.dumps(self.extraSettings["clientConfig"])
        return extraConfigs

    