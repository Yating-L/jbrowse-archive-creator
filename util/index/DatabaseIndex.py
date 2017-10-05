#!/usr/bin/python

import collections
from ExternIndex import ExternIndex

class DatabaseIndex(ExternIndex):
    def __init__(self, database, **args):
        self.database = database
        self.seqType=args.get("seqType")
        self.useIframe=args.get("useIframe")
        self.iframeHeight=args.get("iframeHeight")
        self.iframeWidth=args.get("iframeWidth")

    def setExtLink(self):
        return self.setDatabaseLink(self.database, self.seqType, self.useIframe, self.iframeHeight, self.iframeWidth)

    
    def setDatabaseLink(self, database, seqType=None, useIframe=None, iframeHeight=None, iframeWidth=None):
        database_settings = collections.OrderedDict()
        if "NCBI" in database:
            if not seqType:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/gquery/?term=$$"
            elif seqType == 2:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/protein/$$"
            elif seqType == 1:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/nuccore/$$"
            else:
                raise Exception("Sequence Type {0} is not valid, should be either protein (seqType==2) or nucleotide (seqType==1). Stopping the application".format(seqType))
        elif "UniProt" in database:
            database_settings["url"] = "http://www.uniprot.org/uniprot/$$"
        elif "FlyBase" in database:
            database_settings["url"] = "http://flybase.org/reports/$$"
        else:
            database_settings["url"] = "https://www.ncbi.nlm.nih.gov/gquery/?term=$$"
        database_settings["urlLabel"] = database + " Details:"
        if useIframe or useIframe is None:
            database_settings["iframeUrl"] = database_settings["url"]
            if not iframeHeight:
                iframeHeight = "600"
            if not iframeWidth:
                iframeWidth = "800"
            database_settings["iframeOptions"] = "height= %s width= %s" % (iframeHeight, iframeWidth)
        return database_settings
        
