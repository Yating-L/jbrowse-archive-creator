#!/usr/bin/python

import collections
from ExternIndex import ExternIndex

class DatabaseIndex(ExternIndex):
    def __init__(self, database, **args):
        self.database = database
        self.seqType=args.get("seqType")


    def setExtLink(self):
        return self.setDatabaseLink(self.database, self.seqType)

    
    def setDatabaseLink(self, database, seqType=None):
        database_settings = collections.OrderedDict()
        database_settings.update({"label": "View feature details in the database",
                                  "action": "iframeDialog",
                                  "iconClass": "dijitIconDatabase",
                                  "title": "feature {name}"})

        if "NCBI" in database:
            if not seqType:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/gquery/?term={name}"
            elif seqType == 2:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/protein/{name}"
            elif seqType == 1:
                database_settings["url"] = "https://www.ncbi.nlm.nih.gov/nuccore/{name}"
            else:
                raise Exception("Sequence Type {0} is not valid, should be either protein (seqType==2) or nucleotide (seqType==1). Stopping the application".format(seqType))
        elif "UniProt" in database:
            database_settings["url"] = "http://www.uniprot.org/uniprot/{name}"
        elif "FlyBase" in database:
            database_settings["url"] = "http://flybase.org/reports/{name}"
        else:
            database_settings["url"] = "https://www.ncbi.nlm.nih.gov/gquery/?term={name}"
        return database_settings
        
