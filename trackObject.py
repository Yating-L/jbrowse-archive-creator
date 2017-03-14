#!/usr/bin/env python

import os
import shutil
import utils
import bedToGff3
import blastxmlToGff3

class trackObject:
    def __init__(self, chrom_size, genome, extra_files_path):
        self.chrom_size = chrom_size
        outputDirect = os.path.join(extra_files_path, genome)
        self.raw_folder = os.path.join(outputDirect, 'raw')
        print self.raw_folder
        self.tracks = []
        try:
            if os.path.exists(self.raw_folder):
                if os.path.isdir(self.raw_folder):
                    shutil.rmtree(self.raw_folder)
                else:
                    os.remove(self.raw_folder)
            os.makedirs(self.raw_folder)
        except OSError as oserror:
            print "Cannot create raw folder error({0}): {1}".format(oserror.errno, oserror.strerror)

    def addToRaw(self, dataFile, dataType):
        '''
        Convert gff3, BED, blastxml and gtf files into gff3 files 
        and store converted files in folder 'raw'
        '''
        fileName = os.path.basename(dataFile)
        des_path = os.path.join(self.raw_folder, fileName)
        if dataType == 'gff3_mrna' or dataType == 'gff3_transcript' or dataType == 'fasta' or dataType == 'bam' or dataType == 'bigwig' or dataType == 'bai':
            try:
                shutil.copyfile(dataFile, des_path)
            except shutil.Error as err1:
                print "Cannot move file, error({0}: {1})".format(err1.errno, err1.strerror)
            except IOError as err2:
                print "Cannot move file, error({0}: {1})".format(err2.errno, err2.strerror)
        elif dataType == 'bedSimpleRepeats':
            bedToGff3.bedToGff3(dataFile, self.chrom_size, 'trfbig', des_path)
        elif dataType == 'bedSpliceJunctions':
            bedToGff3.bedToGff3(dataFile, self.chrom_size, 'regtools', des_path)
        elif dataType == 'blastxml':
            blastxmlToGff3.blastxml2gff3(dataFile, des_path)
        elif dataType == 'gtf':
            utils.gtfToGff3(dataFile, des_path, self.chrom_size)
        track = {
            'fileName': fileName,
            'dataType': dataType
        }
        self.tracks.append(track)



'''
    def checkGff3(self, dataFile, dataType):
        with open(dataFile, 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    seq_type = line.rstrip().split('\t')[2]
                    if seq_type == 'transcript':
                        return 'gff3-transcript'
                    if seq_type == 'mRNA':
                        return 'gff3'
'''