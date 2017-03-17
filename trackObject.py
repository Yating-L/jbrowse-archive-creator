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

    def addToRaw(self, dataFile, dataType, metaData):
        """
        Convert gff3, BED, blastxml and gtf files into gff3 files 
        and store converted files in folder 'raw'
        """
        
        fileName = os.path.basename(dataFile)
        des_path = os.path.join(self.raw_folder, fileName)
        track = {}
        if dataType == 'gff3_mrna' or dataType == 'gff3_transcript' or dataType == 'fasta' or dataType == 'bam' or dataType == 'bigwig' or dataType == 'bai':
            if dataType == 'bam':
                # JBrowse will raise error: not a BAM file if the filename hasn't .bam extension
                fileName = os.path.basename(dataFile) + '.bam'
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
        self.SetMetadata(track, metaData)
        self.tracks.append(track)

    #If the metadata is not set, use the default value
    def SetMetadata(self, track, metaData):
        track.update(metaData)
        if 'name' not in metaData.keys() or track['name'] == '':
            track['name'] = track['fileName']
        if 'label' not in metaData.keys() or track['label'] == '':
            track['label'] = track['name']
        if 'track_color' not in metaData.keys() or track['track_color'] == '':
            track['track_color'] = "#daa520"
        if track['dataType'] == 'bigwig':
            if 'pos_color' not in metaData.keys() or track['pos_color'] == '':
                track['pos_color'] = "#FFA600"
            if 'neg_color' not in metaData.keys() or track['neg_color'] == '':
                track['neg_color'] = "#005EFF"
