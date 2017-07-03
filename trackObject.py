#!/usr/bin/env python

import os
import shutil
import utils
import bedToGff3
import blastxmlToGff3


class trackObject:
    def __init__(self, chrom_size, genome, extra_files_path):
        self.chrom_size = chrom_size
        outputDirect = os.path.join(extra_files_path, 'myHub')
        self.raw_folder = os.path.join(outputDirect, 'raw')
        #Store metadata of the tracks
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
        """
        Convert gff3, BED, blastxml and gtf files into gff3 files 
        and store converted files in folder 'raw'
        """
        false_path = os.path.abspath(dataFile)
        fileName = os.path.basename(dataFile)
        des_path = os.path.join(self.raw_folder, fileName)
        track = {}
        if dataType == 'bed' or dataType == 'gff3' or dataType == 'gff3_mrna' or dataType == 'gff3_transcript' or dataType == 'fasta' or dataType == 'bam' or dataType == 'bigwig':
            if dataType == 'bam':
                # JBrowse will raise error: not a BAM file if the filename hasn't .bam extension
                extension = os.path.splitext(fileName)[1]
                if extension != '.bam':
                    fileName = fileName + '.bam'
                des_path = os.path.join(self.raw_folder, fileName)
                bam_index = utils.createBamIndex(dataFile)
                indexname = os.path.basename(bam_index)
                des_path_for_index = os.path.join(self.raw_folder, indexname)
                shutil.copyfile(bam_index, des_path_for_index)  
                track['index'] = indexname

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
        track['fileName'] = fileName
        track['dataType'] = dataType
        track['false_path'] = false_path
        #self.SetMetadata(track, metaData)
        self.tracks.append(track)

    