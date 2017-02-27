#!/usr/bin/env python

'''
Convert BED format to gff3
'''
import os
from collections import OrderedDict
import utils

class bedToGff3():
    def __init__(self, inputBedFile, chrom_sizes, bed_type, output):
        self.input = inputBedFile
        #file_dir = os.path.basename(inputBedFile)
        #print file_dir + "\n\n"
        self.output = output
        self.chrom_sizes = chrom_sizes
        self.type = bed_type
        if self.type == "trfbig":
            self.trfbig_to_gff3()
        if self.type == "regtools":
            self.splicejunctions_to_gff3()

    def trfbig_to_gff3(self):
        gff3 = open(self.output, 'w')
        gff3.write("##gff-version 3\n")
        sizes_dict = utils.sequence_region(self.chrom_sizes)
        seq_regions = dict()
        with open(self.input, 'r') as bed:
            for line in bed:
                field = OrderedDict()
                attribute = OrderedDict()
                li = line.rstrip().split("\t")
                field['seqid'] = li[0]
                if field['seqid'] not in seq_regions:
                    end_region = sizes_dict[field['seqid']]
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                    seq_regions[field['seqid']] = end_region
                field['source'] = li[3]
                field['type'] = 'tandem_repeat'
                # The first base in a chromosome is numbered 0 in BED format
                field['start'] = str(int(li[1]) + 1)
                field['end'] = li[2]
                field['score'] = li[9]
                field['strand'] = '+'
                field['phase'] = '.'
                attribute['length of repeat unit'] = li[4]
                attribute['mean number of copies of repeat'] = li[5]
                attribute['length of consensus sequence'] = li[6]
                attribute['percentage match'] = li[7]
                attribute['percentage indel'] = li[8]
                attribute['percent of a\'s in repeat unit'] = li[10]
                attribute['percent of c\'s in repeat unit'] = li[11]
                attribute['percent of g\'s in repeat unit'] = li[12]
                attribute['percent of t\'s in repeat unit'] = li[13]
                attribute['entropy'] = li[14]
                attribute['sequence of repeat unit element'] = li[15]
                utils.write_features(field, attribute, gff3)
        gff3.close()


    def splicejunctions_to_gff3(self):
        gff3 = open(self.output, 'w')
        gff3.write("##gff-version 3\n")
        sizes_dict = utils.sequence_region(self.chrom_sizes)
        seq_regions = dict()
        with open(self.input, 'r') as bed:
            for line in bed:
                field = OrderedDict()
                attribute = OrderedDict()
                li = line.rstrip().split("\t")
                field['seqid'] = li[0]
                if field['seqid'] not in seq_regions:
                    end_region = sizes_dict[field['seqid']]
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                    seq_regions[field['seqid']] = end_region
                field['source'] = li[3]
                field['type'] = 'junction'
                # The first base in a chromosome is numbered 0 in BED format
                field['start'] = int(li[1]) + 1
                field['end'] = li[2]
                field['score'] = li[12]
                field['strand'] = li[5]
                field['phase'] = '.'
                attribute['ID'] = li[3]
                attribute['Name'] = li[3]
                attribute['blockcount'] = li[9]
                attribute['blocksizes'] = li[10]
                attribute['chromstarts'] = li[11]
                utils.write_features(field, attribute, gff3)
                utils.child_blocks(field, attribute, gff3)
        gff3.close()
        