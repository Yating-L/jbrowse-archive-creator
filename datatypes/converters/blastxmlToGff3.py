#!/usr/bin/env python


from Bio.Blast import NCBIXML
from collections import OrderedDict
from util import subtools


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
    gff3 = open(gff3_file, 'a')
    gff3.write("##gff-version 3\n")
    seq_regions = dict()
    for blast_record in blast_records:
        query_name = blast_record.query.split(" ")[0]
        source = blast_record.application
        method = blast_record.matrix
        for alignment in blast_record.alignments:
            group = {
            "parent_field" : OrderedDict(),
            "parent_attribute" : OrderedDict(),
            "alignments" : []
            }
            title = alignment.title.split(" ")
            contig_name = title[len(title) - 1]
            length = alignment.length
            group['parent_field']['seqid'] = contig_name
            group['parent_field']['source'] = source
            group['parent_field']['type'] = 'match'
            group['parent_attribute']['ID'] = contig_name + '_' + query_name
            group['parent_attribute']['Name'] = query_name
            group['parent_attribute']['method'] = method
            group['parent_attribute']['length'] = length
            if contig_name not in seq_regions:
                gff3.write("##sequence-region " + contig_name + ' 1 ' + str(length) + '\n')
                seq_regions[contig_name] = length
            match_num = 0
            coords = [length, 0]
            for hsp in alignment.hsps:
                hsp_align = {}
                field = OrderedDict()
                attribute = OrderedDict()
                ref = hsp.sbjct
                query = hsp.query
                field['seqid'] = contig_name
                field['source'] = source
                field['type'] = 'match_part'
                
                field['start'] = hsp.sbjct_start
                if field['start'] < coords[0]:
                    coords[0] = field['start']
                ref_length = len(ref.replace('-', ''))
                # if run tblastn, the actual length of reference should be multiplied by 3
                if source.lower() == "tblastn":
                    ref_length *= 3
                field['end'] = field['start'] + ref_length - 1
                if field['end'] > coords[1]:
                    coords[1] = field['end']
                field['score'] = hsp.score
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
                attribute['ID'] = group['parent_attribute']['ID'] + '_match_' + str(match_num)
                attribute['Parent'] = group['parent_attribute']['ID']
                attribute['Target'] = query_name + " " + str(target_start) + " " + str(target_end)
                attribute['Gap'] = align2cigar(query, ref)
                #store the query sequence and match string in the file in order to display alignment with BlastAlignment plugin
                attribute['subject'] = hsp.sbjct
                attribute['query'] = hsp.query
                attribute['match'] = hsp.match
                attribute['gaps'] = attribute['match'].count(' ')
                similar = attribute['match'].count('+')
                attribute['identities'] = len(attribute['match']) - similar - attribute['gaps']
                attribute['positives'] = attribute['identities'] + similar
                attribute['expect'] = hsp.expect
                # show reading frame attribute only if the frame is not (0, 0)
                attribute['frame'] = hsp.frame[1]
                match_num += 1
                hsp_align['field'] = field
                hsp_align['attribute'] = attribute
                group['alignments'].append(hsp_align)
            group['parent_field']['start'] = coords[0]
            group['parent_field']['end'] = coords[1]
            group['parent_field']['score'] = group['parent_field']['strand'] = group['parent_field']['phase'] = '.'
            group['parent_attribute']['match_num'] = match_num
            group['alignments'].sort(key=lambda x: (x['field']['start'], x['field']['end']))
            subtools.write_features(group['parent_field'], group['parent_attribute'], gff3)
            prev_end = -1
            for align in group['alignments']:
                overlap = ''
                if align['field']['start'] <= prev_end:
                    overlap += str(align['field']['start']) + ',' + str(prev_end)
                prev_end = align['field']['end']
                align['attribute']['overlap'] = overlap
                subtools.write_features(align['field'], align['attribute'], gff3)
    gff3.close()

def blastxmlToGff3(xml_file, gff3_file):
    result_handle = open(xml_file)
    blast_records = NCBIXML.parse(result_handle)
    gff3_writer(blast_records, gff3_file)

if __name__ == "__main__":
    blastxmlToGff3("../dbia3/raw/tblastn_dmel-hits-translation-r6.11.fa_vs_nucleotide_BLAST_database_from_data_3.blastxml", "gff3.txt")
