#!/usr/bin/python
# -*- coding: utf8 -*-

"""
Super Class of the managed datatype
"""

import  logging
from datatypes.Datatype import Datatype


class Interval(Datatype):

    def __init__(self):
        super(Interval, self).__init__()
        self.trackType = Datatype.trackType
        logging.debug("Set default trackType = %s for feature tracks", self.trackType)
        self.trackFileType = "gff"


    def getValidateOptions(self, tab=None, autoSql=None):
        options = dict()
        if tab:
            options["tab"] = tab
        if autoSql:
            options["autoSql"] = autoSql
        return options

    def getConvertType(self):
        if not self.trackFileType or not self.dataType:
            raise ValueError("dataType or trackFileType has not been set!")
        return (self.dataType.lower(), self.trackFileType.lower()) 


    



    