#!/usr/bin/env python
import os
import json
import logging

from TrackDb import TrackDb
from util import subtools
from util import santitizer


class BamFeatures(TrackDb):
    def __init__(self, trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings=None):
        super(BamFeatures, self).__init__(trackName, trackLabel, trackDataURL, trackType, dataType, extraSettings)
 
    def prepareExtraSetting(self):
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

    