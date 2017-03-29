#!/usr/bin/env python

"""
This file include common used functions for converting file format to gff3
"""
from collections import OrderedDict
import json
import subprocess
import os
import tempfile
import string

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

def child_blocks(parent_field, parent_attr, gff3):
    num = 0
    blockcount = int(parent_attr['blockcount'])
    chromstart = parent_attr['chromstarts'].split(',')
    blocksize = parent_attr['blocksizes'].split(',')
    while num < blockcount:
        child_attr = OrderedDict()
        child_field = parent_field
        child_field['type'] = 'exon_junction'
        child_field['start'] = int(chromstart[num]) + int(parent_field['start'])
        child_field['end'] = int(child_field['start']) + int(blocksize[num]) - 1
        child_attr['ID'] = parent_attr['ID'] + '_exon_' + str(num+1)
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

def gtfToGff3(gtf_file, gff3_file, chrom_sizes):
    """
    Covert gtf file output from StringTie to gff3 format
    """
    gff3 = open(gff3_file, 'w')
    gff3.write("##gff-version 3\n")
    sizes_dict = sequence_region(chrom_sizes)
    seq_regions = dict()
    parents = dict()
    with open(gtf_file, 'r') as gtf:
        for line in gtf:
            if line.startswith('#'):
                continue
            field = OrderedDict()
            attribute = OrderedDict()
            li = line.rstrip().split("\t")
            #print li
            field['seqid'] = li[0]
            #print field['seqid']
            if field['seqid'] not in seq_regions:
                end_region = sizes_dict[field['seqid']]
                gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                seq_regions[field['seqid']] = end_region
            field['source'] = li[1]
            field['type'] = li[2]
                # The first base in a chromosome is numbered 0 in BED format
            field['start'] = li[3]
            field['end'] = li[4]
            field['score'] = li[5]
            field['strand'] = li[6]
            field['phase'] = li[7]
            attr_li = li[8].split(';')
            gene_id = attr_li[0].split()[1].strip('"')
            attribute['ID'] = gene_id + '_' + field['type'] + '_' + str(field['start']) + '_' + str(field['end'])
            if field['type'] == 'transcript':
                parents[gene_id] = attribute['ID']
                attribute['transcript_id'] = attr_li[1].split()[1].strip('"')
                attribute['coverage'] = attr_li[2].split()[1].strip('"')
                attribute['fpkm'] = attr_li[3].split()[1].strip('"')
                attribute['tpm'] = attr_li[4].split()[1].strip('"')
            elif field['type'] == 'exon':
                attribute['Parent'] = parents[gene_id]
                attribute['transcript_id'] = attr_li[1].split()[1].strip('"')
                attribute['coverage'] = attr_li[3].split()[1].strip('"')
            write_features(field, attribute, gff3)
    gff3.close()


def sanitize_name(input_name):
    """
    Galaxy will name all the files and dirs as *.dat, 
    the function can replace '.' to '_' for the dirs
    """
    validChars = "_-%s%s" % (string.ascii_letters, string.digits)
    sanitized_name = ''.join([c if c in validChars else '_' for c in input_name])
    return "gonramp_" + sanitized_name

def createBamIndex(bamfile):
    subprocess.call(['samtools', 'index', bamfile])
    filename = bamfile + '.bai'
    if os.path.exists(filename):
        return filename
    else:
        raise ValueError('Did not find bai file')
