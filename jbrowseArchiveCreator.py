#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This Galaxy tool permits to prepare your files to be ready for JBrowse visualization.
"""

import sys
import argparse
import json
import logging
import collections


# Internal dependencies
from util.Reader import Reader
from util.Logger import Logger 
from TrackHub import TrackHub



def main(argv):
    parser = argparse.ArgumentParser(description='Create a hub to display in jbrowse.')
    parser.add_argument('-j', '--data_json', help='JSON file containing the metadata of the inputs')
    parser.add_argument('-o', '--output', help='Name of the HTML summarizing the content of the JBrowse Hub Archive')

    # Get the args passed in parameter
    args = parser.parse_args()
    json_inputs_data = args.data_json
    outputFile = args.output

    ##Parse JSON file with Reader
    reader = Reader(json_inputs_data)

    # Begin init variables
    extra_files_path = reader.getExtFilesPath()
    toolDirectory = reader.getToolDir()
    #outputFile = reader.getOutputDir()
    user_email = reader.getUserEmail()
    reference_genome = reader.getRefGenome()
    debug_mode = reader.getDebugMode()
    track_type = reader.getTrackType()
    #jbrowse_path = reader.getJBrowsePath()
    apollo_host = reader.getApolloHost()
 
    #### Logging management ####
    # If we are in Debug mode, also print in stdout the debug dump
    log = Logger(tool_directory=toolDirectory, debug=debug_mode, extra_files_path=extra_files_path)
    log.setup_logging()
    logging.info('#### JBrowseArchiveCreator: Start ####\n')
    logging.debug('---- Welcome in JBrowseArchiveCreator Debug Mode ----\n')
    logging.debug('JSON parameters: %s\n\n', json.dumps(reader.args))
    #### END Logging management ####

    # Create the Track Hub folder
    logging.info('#### JBrowseArchiveCreator: Creating the Track Hub folder ####\n')
    trackHub = TrackHub(reference_genome, user_email, outputFile, extra_files_path, toolDirectory, track_type, apollo_host)

    # Create Ordered Dictionary to add the tracks in the tool form order
    logging.info('#### JBrowseArchiveCreator: Preparing track data ####\n')
    all_datatype_dictionary = reader.getTracksData()
    all_datatype_ordered_dictionary = collections.OrderedDict(all_datatype_dictionary)

    logging.debug("----- End of all_datatype_dictionary processing -----")
    #logging.debug("all_datatype_ordered_dictionary are: %s", json.dumps(all_datatype_ordered_dictionary))

    logging.info('#### JBrowseArchiveCreator: Adding tracks to Track Hub ####\n')
    logging.debug("----- Beginning of Track adding processing -----")

    for index, datatypeObject in all_datatype_ordered_dictionary.iteritems():
       trackHub.addTrack(datatypeObject.track.track_db)

    logging.debug("----- End of Track adding processing -----")

    # We terminate the process and so create a HTML file summarizing all the files
    logging.info('#### JBrowseArchiveCreator: Creating the HTML file ####\n')
    trackHub.terminate(debug_mode)

    logging.debug('---- End of JBrowseArchiveCreator Debug Mode: Bye! ----\n')
    logging.info('#### JBrowseArchiveCreator: Congratulation! Assembly Hub is created! ####\n')

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)

'''
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

    # blat alignment (bigpsl 12+12)
    parser.add_argument('--bigpsl', action='append', help='bigpsl format from blat alignment')

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
    array_inputs_bigpsl = args.bigpsl

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
    if array_inputs_bigpsl:
        all_datatype_dictionary['bigpsl'] =  array_inputs_bigpsl    
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

                #all_tracks.addToRaw(f, datatype)

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
 def create_ordered_datatype_objects(self, ExtensionClass, array_inputs):
        """
        Function which executes the creation all the necessary files / folders for a special Datatype, for TrackHub
        and update the dictionary of datatype

        :param ExtensionClass:
        :param array_inputs:
        :type ExtensionClass: Datatype
        :type array_inputs: list[string]
        """

        datatype_dictionary = {}

        # TODO: Optimize this double loop
        for input_data in array_inputs:
            input_false_path = input_data["false_path"]
            input_data["name"] = santitizer.sanitize_name_input(input_data["name"])
            extensionObject = ExtensionClass(input_false_path, input_data)
            extensionObject.generateCustomTrack()
            datatype_dictionary.update({input_data["order_index"]: extensionObject})
        return datatype_dictionary

if __name__ == "__main__":
    main(sys.argv)
'''

