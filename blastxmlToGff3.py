#!/usr/bin/env python


from Bio.Blast import NCBIXML
from collections import OrderedDict
import utils


def align2cigar(hsp_query, hsp_reference):
    """
        Build CIGAR representation from an hsp_query
        input:
            hsp_query
            hsp_sbjct
        output:
            CIGAR string
    """
    query = hsp_query
    ref = hsp_reference
    # preType, curType:
    # 'M' represents match,
    # 'I' represents insert a gap into the reference sequence,
    # 'D' represents insert a gap into the target (delete from reference)
    # some ideas of this algin2cigar function are coming from
    # https://gist.github.com/ozagordi/099bdb796507da8d9426
    prevType = 'M'
    curType = 'M'
    count = 0
    cigar = []
    num = len(query)
    for i in range(num):
        if query[i] == '-':
            curType = 'D'
        elif ref[i] == '-':
            curType = 'I'
        else:
            curType = 'M'
        if curType == prevType:
            count += 1
        else:
            cigar.append('%s%d' % (prevType, count))
            prevType = curType
            count = 1
    cigar.append('%s%d' % (curType, count))
    return ' '.join(cigar)

def gff3_writer(blast_records, gff3_file):
    gff3 = open(gff3_file, 'w')
    gff3.write("##gff-version 3\n")
    seq_regions = dict()
    for blast_record in blast_records:
        query_name = blast_record.query.split(" ")[0]
        source = blast_record.application
        for alignment in blast_record.alignments:
            title = alignment.title.split(" ")
            seqid = title[len(title) - 1]
            length = alignment.length
            feature_type = 'match'
            for hsp in alignment.hsps:
                field = OrderedDict()
                attribute = OrderedDict()
                ref = hsp.sbjct
                query = hsp.query
                field['seqid'] = seqid
                field['source'] = source
                field['type'] = feature_type
                if seqid not in seq_regions:
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(length) + '\n')
                    seq_regions[seqid] = length
                field['start'] = hsp.sbjct_start
                ref_length = len(ref.replace('-', ''))
                # if run tblastn, the actual length of reference should be multiplied by 3
                if source.lower() == "tblastn":
                    ref_length *= 3
                field['end'] = field['start'] + ref_length - 1
                field['score'] = hsp.expect
                #decide if the alignment in the same strand or reverse strand
                #reading frame
                # (+, +), (0, 0), (-, -) => +
                # (+, -), (-, +) => -
                if hsp.frame[1] * hsp.frame[0] > 0:
                    field['strand'] = '+'
                elif hsp.frame[1] * hsp.frame[0] < 0:
                    field['strand'] = '-'
                else:
                    if hsp.frame[0] + hsp.frame[1] >= 0:
                        field['strand'] = '+'
                    else:
                        field['strand'] = '-'
                field['phase'] = '.'

                target_start = hsp.query_start
                target_len = len(query.replace('-', ''))
                # if run blastx, the actual length of query should be multiplied by 3
                if source.lower() == "blastx":
                    target_len *= 3
                target_end = target_start + target_len -1
                attribute['ID'] = field['seqid'] + '_' + str(field['start']) + '_' + str(field['end']) + '_' + query_name + '_' + str(target_start) + '_' + str(target_end)
                attribute['Target'] = query_name + " " + str(target_start) + " " + str(target_end)
                attribute['Gap'] = align2cigar(query, ref)
                #store the query sequence in the file in order to display alignment with BlastAlignment plugin
                attribute['query'] = hsp.query
                # show reading frame attribute only if the frame is not (0, 0)
                if hsp.frame[0] != 0 or hsp.frame[1] != 0:
                    attribute['reading_frame'] = str(hsp.frame[0]) + ", " + str(hsp.frame[1])
                utils.write_features(field, attribute, gff3)

def blastxml2gff3(xml_file, gff3_file):
    result_handle = open(xml_file)
    blast_records = NCBIXML.parse(result_handle)
    gff3_writer(blast_records, gff3_file)
    
if __name__ == "__main__":
    blastxml2gff3("../tblastn_dmel.blastxml", "gff3.txt")

