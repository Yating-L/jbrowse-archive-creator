#!/usr/bin/python
"""
Super Class of the tracks
"""
import os
import abc
from abc import ABCMeta
import collections
import json
import logging
from util import santitizer

class TrackDb(object):
    """docstring for TrackDb"""
    __metaclass__ = ABCMeta

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
        #self.createTrackDb()

    def createTrackDb(self):
        self.track_db = collections.OrderedDict([("track",self.trackName),
                ("trackLabel",self.trackLabel),
                ("trackDataURL",self.trackDataURL),
                ("dataType", self.dataType),
                ("trackType", self.trackType)]
                )

        self.track_db["nameIndex"] = self.extraSettings['nameIndex']

        extraConfigs = self.prepareExtraSetting()
        self.logger.debug("Generate extraConfigs = %s", json.dumps(extraConfigs))
        self.track_db["options"] = extraConfigs
        #print self.track_db
        self.logger.debug("TrackDb object is created track_db = %s ", json.dumps(self.track_db))

    @abc.abstractmethod
    def prepareExtraSetting(self):
        """ set optional configurations for the track """
