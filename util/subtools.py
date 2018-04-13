#!/usr/bin/env python

"""
This file include common used functions for converting file format to gff3
"""
from collections import OrderedDict
import json
import subprocess
import os
import sys
import tempfile
import shutil
import logging

class PopenError(Exception):
    def __init__(self, cmd, error, return_code):
        self.cmd = cmd
        self.error = error
        self.return_code = return_code

    def __str__(self):
        message = "The subprocess {0} has returned the error: {1}.".format(
            self.cmd, self.return_code)
        message = ','.join(
            (message, "Its error message is: {0}".format(self.error)))
        return repr(message)


def _handleExceptionAndCheckCall(array_call, **kwargs):
    """
    This class handle exceptions and call the tool.
    It maps the signature of subprocess.check_call:
    See https://docs.python.org/2/library/subprocess.html#subprocess.check_call
    """
    stdout = kwargs.get('stdout', subprocess.PIPE)
    stderr = kwargs.get('stderr', subprocess.PIPE)
    shell = kwargs.get('shell', False)
    stdin = kwargs.get('stdin', None)

    cmd = array_call[0]

    output = None
    error = None

    # TODO: Check the value of array_call and <=[0]
    logging.debug("Calling {0}:".format(cmd))
    logging.debug("%s", array_call)
    logging.debug("---------")

    # TODO: Use universal_newlines option from Popen?
    try:
        p = subprocess.Popen(array_call, stdout=stdout,
                             stderr=stderr, shell=shell, stdin=stdin)

        # TODO: Change this because of possible memory issues => https://docs.python.org/2/library/subprocess.html#subprocess.Popen.communicate

        output, error = p.communicate()

        if stdout == subprocess.PIPE:
            logging.debug("\t{0}".format(output))
        else:
            logging.debug("\tOutput in file {0}".format(stdout.name))
        # If we detect an error from the subprocess, then we raise an exception
        # TODO: Manage if we raise an exception for everything, or use CRITICAL etc... but not stop process
        # TODO: The responsability of returning a sys.exit() should not be there, but up in the app.
        if p.returncode:
            if stderr == subprocess.PIPE:
                raise PopenError(cmd, error, p.returncode)
            else:
                # TODO: To Handle properly with a design behind, if we received a option as a file for the error
                raise Exception("Error when calling {0}. Error as been logged in your file {1}. Error code: {2}"
                                .format(cmd, stderr.name, p.returncode))

    except OSError as e:
        message = "The subprocess {0} has encountered an OSError: {1}".format(
            cmd, e.strerror)
        if e.filename:
            message = '\n'.join(
                (message, ", against this file: {0}".format(e.filename)))
        logging.error(message)
        sys.exit(-1)
    except PopenError as p:
        message = "The subprocess {0} has returned the error: {1}.".format(
            p.cmd, p.return_code)
        message = '\n'.join(
            (message, "Its error message is: {0}".format(p.error)))

        logging.exception(message)

        sys.exit(p.return_code)
    except Exception as e:
        message = "The subprocess {0} has encountered an unknown error: {1}".format(
            cmd, e)
        logging.exception(message)

        sys.exit(-1)
    return p


def write_features(field, attribute, gff3):
    """
    The function write the features to gff3 format (defined in https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md)
    field, attribute are ordered dictionary 
    gff3 is the file handler
    """
    attr = []
    for v in field.values():
        gff3.write(str(v) + '\t')
    for k, v in attribute.items():
        s = str(k) + '=' + str(v)
        attr.append(s)
    gff3.write(';'.join(attr))
    gff3.write('\n')

def twoBitInfo(two_bit_file_name, two_bit_info_file):
    """
    Call twoBitInfo and write the result into twoBit_info_file
    :param two_bit_file_name:
    :param two_bit_info_file:
    :return the subprocess.check_call return object:
    """
    array_call = ['twoBitInfo', two_bit_file_name, two_bit_info_file]
    p = _handleExceptionAndCheckCall(array_call)
    return p


def faToTwoBit(fasta_file_name, twoBitFile):
    """
    This function call faToTwoBit UCSC tool, and return the twoBitFile
    :param fasta_file_name:
    :param mySpecieFolder:
    :return:
    """

    array_call = ['faToTwoBit', fasta_file_name, twoBitFile]
    _handleExceptionAndCheckCall(array_call)

    return twoBitFile

def sortChromSizes(two_bit_info_file_name, chrom_sizes_file_name):
    """
    Call sort with -k2rn on two_bit_info_file_name and write the result into chrom_sizes_file_name
    :param two_bit_info_file_name:
    :param chrom_sizes_file_name:
    :return:
    """
    array_call = ['sort', '-k2rn', two_bit_info_file_name,
                  '-o', chrom_sizes_file_name]
    p = _handleExceptionAndCheckCall(array_call)
    return p

def getChromSizes(reference, tool_dir):
    #TODO: find a better way instead of shipping the two exec files with the tool
    faToTwoBit = os.path.join(tool_dir, 'faToTwoBit')
    twoBitInfo = os.path.join(tool_dir, 'twoBitInfo')
    try:
        twoBitFile = tempfile.NamedTemporaryFile(bufsize=0)
        chrom_sizes = tempfile.NamedTemporaryFile(bufsize=0, suffix='.chrom.sizes', delete=False)
    except IOError as err:
        print "Cannot create tempfile err({0}): {1}".format(err.errno, err.strerror)
    try:
        subprocess.call(['faToTwoBit', reference, twoBitFile.name])
    except OSError as err:
        print "Cannot generate twoBitFile from faToTwoBit err({0}): {1}".format(err.errno, err.strerror)
    try:
        subprocess.call(['twoBitInfo', twoBitFile.name, chrom_sizes.name])
    except OSError as err:
        print "Cannot generate chrom_sizes from twoBitInfo err({0}): {1}".format(err.errno, err.strerror)
    return chrom_sizes

def sequence_region(chrom_sizes):
    """
    This function read from a chromatin size file generated by twoBitInfo and write the information to dict
    return a dict
    """
    f = open(chrom_sizes, 'r')
    sizes = f.readlines()
    sizes_dict = {}
    for line in sizes:
        chrom_info = line.rstrip().split('\t')
        sizes_dict[chrom_info[0]] = chrom_info[1]
    return sizes_dict

def child_blocks(parent_field, parent_attr, gff3, child_type):
    num = 0
    blockcount = int(parent_attr['blockcount'])
    chromstart = parent_attr['chromstarts'].split(',')
    blocksize = parent_attr['blocksizes'].split(',')
    parent_start = parent_field['start']
    while num < blockcount:
        child_attr = OrderedDict()
        child_field = parent_field
        child_field['type'] = child_type
        child_field['start'] = int(chromstart[num]) + int(parent_start)
        child_field['end'] = int(child_field['start']) + int(blocksize[num]) - 1
        child_attr['ID'] = parent_attr['ID'] + '_part_' + str(num+1)
        child_attr['Parent'] = parent_attr['ID']
        write_features(child_field, child_attr, gff3)
        num = num + 1

def add_tracks_to_json(trackList_json, new_tracks, modify_type):
    """
    Add to track configuration (trackList.json)
    # modify_type =  'add_tracks': add a new track like bam or bigwig, new_track = dict()
    # modify_type = 'add_attr': add configuration to the existing track, new_track = dict(track_name: dict())
    """
    with open(trackList_json, 'r+') as f:
        data = json.load(f)
        if modify_type == 'add_tracks':
            data['tracks'].append(new_tracks)
        elif modify_type == 'add_attr':
            for k in new_tracks:
                for track in data['tracks']:
                    if k.lower() in track['urlTemplate'].lower():
                        attr = new_tracks[k]
                        for k, v in attr.items():
                            track[k] = v
        f.seek(0, 0)
        f.write(json.dumps(data, separators=(',' , ':'), indent=4))
        f.truncate()
        f.close()


def createBamIndex(bamfile):
    subprocess.call(['samtools', 'index', bamfile])
    filename = bamfile + '.bai'
    if os.path.exists(filename):
        return filename
    else:
        raise ValueError('Did not find bai file')

def createFastaIndex(fastaFile):
    subprocess.call(['samtools', 'faidx', fastaFile])
    filename = fastaFile + '.fai'
    if os.path.exists(filename):
        return filename
    else:
        raise ValueError('Did not find fai file')

def generate_indexed_refseq_track(fastaFile, referenceName, outputFolder):
    faiFile = createFastaIndex(fastaFile)
    refSeqFile = os.path.join(outputFolder, referenceName)
    refSeqIndexFile = os.path.join(outputFolder, referenceName+'.fai')
    shutil.copy(fastaFile, refSeqFile)
    shutil.copy(faiFile, refSeqIndexFile)

def remove_gene_lines(gff3_file, gff3_filtered):
    with open(gff3_file, 'r') as f:
        with open(gff3_filtered, 'w') as out:
            for line in f:
                if not line.startswith('#'):
                    feature_type = line.split('\t')[2].rstrip()
                    if feature_type == 'transcript' or feature_type == 'mRNA':
                        arr = line.split('\t')
                        # as we remove the gene features, we should also remove the Parent attribute (gene id) from the transcript
                        arr[8] = ';'.join([item for item in arr[8].split(';') if 'Parent=' not in item]).rstrip()
                        line = '\t'.join(arr) + '\n'
                    if feature_type == 'gene':
                        continue
                out.write(line)

def gff3sort(inputFile, outputFile, precise=False):
    array_call = ['gff3sort.pl', inputFile]
    if precise:
        array_call.append('--precise')
    p = _handleExceptionAndCheckCall(array_call, stdout=outputFile)
    return p

def bedSort(inputFile, outputFile):
    array_call = ['sort', '-k1,1', '-k2,2n', '-k6,6', inputFile]
    p = _handleExceptionAndCheckCall(array_call, stdout=outputFile)
    return p

def bgzip(inputFile):
    subprocess.call(['bgzip', inputFile])
    filename = inputFile + '.gz'
    if os.path.exists(filename):
        return filename
    else:
        raise ValueError('Did not find gz file')

def createTabix(inputFile, dataType):
    subprocess.call(['tabix', '-p', dataType, inputFile])
    filename = inputFile + '.tbi'
    if os.path.exists(filename):
        return filename
    else:
        raise ValueError('Did not find tbi file')

def generate_tabix_indexed_track(inputFile, dataType, trackName, outputFolder):
    if "bed" in dataType:
        fileType = 'bed'
        sortedFile = tempfile.NamedTemporaryFile(bufsize=0)
        bedSort(inputFile, sortedFile)
    elif "gff" in dataType:
        fileType = 'gff'
        filteredFile = tempfile.NamedTemporaryFile(bufsize=0)
        remove_gene_lines(inputFile, filteredFile.name)
        sortedFile = tempfile.NamedTemporaryFile(bufsize=0)
        gff3sort(filteredFile.name, sortedFile)
        # add .gff3.gz extension to Tabix GFF3 files, in order to enable creating name index with generate-names.pl
        trackName = trackName + '.gff3.gz'
    compressedFile = bgzip(sortedFile.name)
    tabixFile = createTabix(compressedFile, fileType)
    trackPath = os.path.join(outputFolder, trackName)
    trackIndexPath = os.path.join(outputFolder, trackName+'.tbi')
    shutil.copy(compressedFile, trackPath)
    shutil.copy(tabixFile, trackIndexPath)

def flatfile_to_json(inputFile, dataType, trackType, trackLabel, outputFolder, options=None, compress=True):
    if "bed" in dataType:
        fileType = "--bed"
    elif "gff" in dataType:
        fileType = "--gff"
    else:
        raise ValueError("%s is not a valid filetype for flatfile_to_json" % dataType)
       

    array_call = ['flatfile-to-json.pl', 
                   fileType, inputFile, 
                   '--trackType', trackType, 
                   '--trackLabel', trackLabel,
                   '--out', outputFolder]
    if compress:
        array_call.append('--compress')
    if options:
        config = options.get("config")
        clientConfig = options.get("clientConfig")
        renderClassName = options.get('renderClassName')
        subfeatureClasses = options.get('subfeatureClasses')
        load_type = options.get("type")
        if clientConfig:
            array_call.append('--clientConfig')
            array_call.append(clientConfig)
        if config:
            array_call.append('--config')
            array_call.append(config)
        if load_type:
            array_call.append('--type')
            array_call.append(load_type)
        if renderClassName:
            array_call.append('--renderClassName')
            array_call.append(renderClassName)
        if subfeatureClasses:
            array_call.append('--subfeatureClasses')
            array_call.append(json.dumps(subfeatureClasses))

    p = _handleExceptionAndCheckCall(array_call)
    return p

def bam_to_json(inputFile, trackLabel, outputFolder, options=None, compress=False):
    
    array_call = ['bam-to-json.pl', 
                   '--bam', inputFile, 
                   '--trackLabel', trackLabel,
                   '--out', outputFolder]
    if compress:
        array_call.append('--compress')
    if options:
        config = options.get('config')
        clientConfig = options.get('clientConfig')
        if clientConfig:
            array_call.append('--clientConfig')
            array_call.append(clientConfig)
        if config:
            array_call.append('--config')
            array_call.append(config)

    p = _handleExceptionAndCheckCall(array_call)
    return p

def add_track_json(trackList, track_json):
    track_json = json.dumps(track_json)
    new_track = subprocess.Popen(['echo', track_json], stdout=subprocess.PIPE)
    p = subprocess.call(['add-track-json.pl', trackList], stdin=new_track.stdout)
    return p

def prepare_refseqs(fastaFile, outputFolder):
    #array_call = ['prepare-refseqs.pl', '--fasta', fasta_file_name, '--out', outputFolder]
    createFastaIndex(fastaFile)
    array_call = ['prepare-refseqs.pl', '--indexed_fasta', fastaFile, '--out', outputFolder]
    p = _handleExceptionAndCheckCall(array_call)
    return p       

def generate_names(outputFolder, hashBits=4):
    array_call = ['generate-names.pl', '--hashBits', '4', '-v', '--out', outputFolder]
    p = _handleExceptionAndCheckCall(array_call)
    return p  
   
def validateFiles(input_file, chrom_sizes_file_name, file_type, options=None):
    """
    Call validateFiles on input_file, using chrom_sizes_file_name and file_type
    :param input_file:
    :param chrom_sizes_file_name:
    :param file_type:
    :return:
    """
    
    array_call = ['validateFiles', '-chromInfo=' + chrom_sizes_file_name, '-type='+ file_type, input_file]
    if options:
        tab = options.get("tab")
        autoSql = options.get("autoSql")
        logging.debug("tab: {0}".format(tab))
        logging.debug("autoSql: {0}".format(autoSql))
        if autoSql:
            autoSql = ''.join(['-as=', autoSql])
            array_call.append(autoSql)
        if tab:
            array_call.append('-tab')
    p = _handleExceptionAndCheckCall(array_call)
    return p

