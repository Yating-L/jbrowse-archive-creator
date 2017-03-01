#!/usr/bin/env python

import os
import shutil
import utils
import bedToGff3
import blastxmlToGff3

class trackObject:
    def __init__(self, dataFile, dataType, chrom_size):
        self.dataFile = dataFile
        self.fileName = os.path.basename(dataFile)
        self.dataType = dataType
        self.chrom_size = chrom_size
        try:
            if not os.path.exists('raw'):
                os.mkdir('raw')
        except OSError as oserror:
            print "Cannot create raw folder error({0}): {1}".format(oserror.errno, oserror.strerror)
        else:
            self.raw_folder = 'raw'

    def addToRaw(self):
        des_path = os.path.join(self.raw_folder, self.fileName)
        if self.dataType == 'gff3' or self.dataType == 'fasta' or self.dataType == 'bam' or self.dataType == 'bigwig' or self.dataType == 'bai':
            if self.dataType == 'gff3':
                self.checkGff3()
            try:
                shutil.copyfile(self.dataFile, des_path)
            except shutil.Error as err1:
                print "Cannot move file, error({0}: {1})".format(err1.errno, err1.strerror)
            except IOError as err2:
                print "Cannot move file, error({0}: {1})".format(err2.errno, err2.strerror)
        elif self.dataType == 'bedSimpleRepeats':
            bedToGff3.bedToGff3(self.dataFile, self.chrom_size, 'trfbig', des_path)
        elif self.dataType == 'bedSpliceJunctions':
            bedToGff3.bedToGff3(self.dataFile, self.chrom_size, 'regtools', des_path)
        elif self.dataType == 'blastxml':
            blastxmlToGff3.blastxml2gff3(self.dataFile, des_path)
        elif self.dataType == 'gtf':
            utils.gtfToGff3(self.dataFile, des_path, self.chrom_size)

    def checkGff3(self):
        with open(self.dataFile, 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    seq_type = line.rstrip().split('\t')[2]
                    if seq_type == 'transcript':
                        self.dataType = 'gff3-transcript'
                        break
                    if seq_type == 'mRNA':
                        break
