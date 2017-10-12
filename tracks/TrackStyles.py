#!/usr/bin/env python
import os
import json
import logging
from mako.lookup import TemplateLookup

class TrackStyles(object):
    def __init__(self, tool_directory, species_folder, trackListFile, cssFolderName="css", cssFileName="custom_track_styles.css"):
        self.logger = logging.getLogger(__name__)
        self.tool_directory = tool_directory
        self.species_folder = species_folder
        self.trackList = trackListFile
        self.cssFolderName = cssFolderName
        self.cssFileName = cssFileName
        self.cssFilePath = self._createCssFile()
        self.cssTemplate = self._getCssTemplate()
        self._addCssToTrackList()
        

    def addCustomColor(self, feature_class_name, feature_color):
        with open(self.cssFilePath, 'a+') as css:
            htmlMakoRendered = self.cssTemplate.render(
            label = feature_class_name,
            color = feature_color
        )
            css.write(htmlMakoRendered)
        self.logger.debug("create customized track css class: cssFilePath= %s", self.cssFilePath)
   

    def _createCssFile(self):
        cssFolderPath = os.path.join(self.species_folder, self.cssFolderName)
        cssFilePath = os.path.join(cssFolderPath, self.cssFileName)
        if not os.path.exists(cssFilePath):
            if not os.path.exists(cssFolderPath):
                os.mkdir(cssFolderPath)
            os.mknod(cssFilePath)   
        return cssFilePath

    def _getCssTemplate(self):
        mylookup = TemplateLookup(directories=[os.path.join(self.tool_directory, 'templates')],
                                  output_encoding='utf-8', encoding_errors='replace')
        cssTemplate = mylookup.get_template("custom_track_styles.css")
        return cssTemplate

    
    def _addCssToTrackList(self):
        with open(self.trackList, 'r+') as track:
            data = json.load(track)
            css_path = os.path.join('data', self.cssFolderName, self.cssFileName)
            data['css'] = {'url': css_path}
            json_string = json.dumps(data, indent=4, separators=(',', ': '))
            track.seek(0)
            track.write(json_string)
            track.truncate()
        self.logger.debug("added customized css url to trackList.json")
        

    