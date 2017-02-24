#!/usr/bin/env python

'''
Convert BED format to gff3
'''
import os
from collections import OrderedDict
import utils

def gtfToGff3(gtf_file, gff3_file, chrom_sizes):
    gff3 = open(gff3_file, 'w')
    gff3.write("##gff-version 3\n")
    sizes_dict = utils.sequence_region(chrom_sizes)
    seq_regions = dict()
    parents = dict()
    with open(gtf_file, 'r') as gtf:
        for line in gtf:
            if line.startswith('#'):
                continue
            field = OrderedDict()
            attribute = OrderedDict()
            li = line.rstrip().split("\t")
            print li
            field['seqid'] = li[0]
            print field['seqid']
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
            utils.write_features(field, attribute, gff3)

if __name__ == "__main__":
    gtfToGff3("dbia3/raw/StringTie_on_data_15__Assembled_transcripts.gtf", "stringtie.gff3", "dbia3/raw/dbia3.sizes")


