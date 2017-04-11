#!/usr/bin/env python

import sys
import argparse
import json
import utils
import trackObject
import TrackHub



def main(argv):
    parser = argparse.ArgumentParser(description='Create a hub to display in jbrowse.')

    # Reference genome mandatory
    parser.add_argument('-f', '--fasta', help='Fasta file of the reference genome (Required)')

    # Genome name
    parser.add_argument('-g', '--genome_name', help='Name of reference genome')

    # Output folder
    parser.add_argument('-o', '--out', help='output html')

    # Output folder
    parser.add_argument('-e', '--extra_files_path', help='Directory of JBrowse Hub folder')

    #Tool Directory
    parser.add_argument('-d', '--tool_directory', help='The directory of JBrowse file convertion scripts and UCSC tools')

    #GFF3
    parser.add_argument('--gff3', action='append', help='GFF3 format')

    # GFF3 structure: gene->transcription->CDS
    parser.add_argument('--gff3_transcript', action='append', help='GFF3 format for gene prediction, structure: gene->transcription->CDS')

    # GFF3 structure: gene->mRNA->CDS
    parser.add_argument('--gff3_mrna', action='append', help='GFF3 format for gene prediction, structure: gene->mRNA->CDS')

    # generic BED 
    parser.add_argument('--bed', action='append', help='BED format')

    # trfBig simple repeats (BED 4+12)
    parser.add_argument('--bedSimpleRepeats', action='append', help='BED 4+12 format, using simpleRepeats.as')

    # regtools (BED 12+1)
    parser.add_argument('--bedSpliceJunctions', action='append', help='BED 12+1 format, using spliceJunctions.as')

    # tblastn alignment (blastxml)
    parser.add_argument('--blastxml', action='append', help='blastxml format from tblastn')

    # BAM format
    parser.add_argument('--bam', action='append', help='BAM format from HISAT')

    # BIGWIG format
    parser.add_argument('--bigwig', action='append', help='BIGWIG format to show rnaseq coverage')

    # GTF format
    parser.add_argument('--gtf', action='append', help='GTF format from StringTie')

    # Metadata json format
    parser.add_argument('-j', '--data_json', help='Json containing the metadata of the inputs')

    #JBrowse host
    parser.add_argument('--jbrowse_host', help="JBrowse Host")

    args = parser.parse_args()
    all_datatype_dictionary = dict()
    

    if not args.fasta:
        parser.print_help()
        raise RuntimeError("No reference genome\n")
    reference = args.fasta
    genome = 'unknown'
    out_path = 'unknown.html'
    extra_files_path = '.'
    tool_directory = '.'
    jbrowse_host = ''
    if args.jbrowse_host:
        jbrowse_host = args.jbrowse_host
    if args.genome_name:
        genome = args.genome_name
    if args.out:
        out_path = args.out
    if args.extra_files_path:
        extra_files_path = args.extra_files_path

    #tool_directory not work for Galaxy tool, all tools need to exist in the current PATH, deal with it with tool dependencies
    if args.tool_directory:
        tool_directory = args.tool_directory

    #Calculate chromsome sizes using genome reference and uscs tools
    chrom_size = utils.getChromSizes(reference, tool_directory)

    #get metadata from json file
    json_inputs_data = args.data_json
    if json_inputs_data:
        inputs_data = json.loads(json_inputs_data)
    else:
        inputs_data = {}
    
    #print inputs_data

    #Initate trackObject
    all_tracks = trackObject.trackObject(chrom_size.name, genome, extra_files_path) 
    
    array_inputs_bam = args.bam
    array_inputs_bed = args.bed
    array_inputs_bed_simple_repeats = args.bedSimpleRepeats
    array_inputs_bed_splice_junctions = args.bedSpliceJunctions
    array_inputs_bigwig = args.bigwig
    array_inputs_gff3 = args.gff3
    array_inputs_gff3_transcript = args.gff3_transcript
    array_inputs_gff3_mrna = args.gff3_mrna
    array_inputs_gtf = args.gtf
    array_inputs_blastxml = args.blastxml

    if array_inputs_bam:
        all_datatype_dictionary['bam'] = array_inputs_bam
    if array_inputs_bed:
        all_datatype_dictionary['bed'] = array_inputs_bed
    if array_inputs_bed_simple_repeats:
        all_datatype_dictionary['bedSimpleRepeats'] = array_inputs_bed_simple_repeats
    if array_inputs_bed_splice_junctions:
        all_datatype_dictionary['bedSpliceJunctions'] = array_inputs_bed_splice_junctions
    if array_inputs_bigwig:
        all_datatype_dictionary['bigwig'] = array_inputs_bigwig
    if array_inputs_gff3:
        all_datatype_dictionary['gff3'] = array_inputs_gff3
    if array_inputs_gff3_transcript:
        all_datatype_dictionary['gff3_transcript'] = array_inputs_gff3_transcript
    if array_inputs_gff3_mrna:
        all_datatype_dictionary['gff3_mrna'] = array_inputs_gff3_mrna
    if array_inputs_gtf:
        all_datatype_dictionary['gtf'] = array_inputs_gtf
    if array_inputs_blastxml:
        all_datatype_dictionary['blastxml'] = array_inputs_blastxml
    
    print "input tracks: \n", all_datatype_dictionary

    for datatype, inputfiles in all_datatype_dictionary.items():
        try:
            if not inputfiles:
                raise ValueError('empty input, must provide track files!\n')
        except IOError:
            print 'Cannot open', datatype
        else:
            for f in inputfiles:
                #metadata = {}
                #print f
                #if f in inputs_data.keys():
                   # metadata = inputs_data[f]
                    #print metadata
                #Convert tracks into gff3 format
                all_tracks.addToRaw(f, datatype)

    jbrowseHub = TrackHub.TrackHub(all_tracks, reference, out_path, tool_directory, genome, extra_files_path, inputs_data, jbrowse_host)
    jbrowseHub.createHub()

"""        
def extractMetadata(array_inputs, inputs_data):
    metadata_dict = {}
    for input_false_path in array_inputs:
        for key, data_value in inputs_data.items():
            if key == input_false_path:
                metadata_dict[input_false_path]
"""

if __name__ == "__main__":
    main(sys.argv)

