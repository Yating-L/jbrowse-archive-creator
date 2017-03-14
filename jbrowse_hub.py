#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from bedToGff3 import bedToGff3
import blastxmlToGff3
import utils
import tempfile
import trackObject
import TrackHub
import shutil

def main(argv):
    parser = argparse.ArgumentParser(description='Create a hub to display in jbrowse.')

    # Reference genome mandatory
    parser.add_argument('-f', '--fasta', help='Fasta file of the reference genome')

    # Genome name
    parser.add_argument('-g', '--genome_name', help='Name of reference genome')

    # Output folder
    parser.add_argument('-o', '--out', help='output html')

    # Output folder
    parser.add_argument('-e', '--extra_files_path', help="Directory of JBrowse Hub folder")

    # GFF3 structure: gene->transcription->CDS
    parser.add_argument('--gff3_transcript', action='append', help='GFF3 format, structure: gene->transcription->CDS')

    # GFF3 structure: gene->mRNA->CDS
    parser.add_argument('--gff3_mrna', action='append', help='GFF3 format, structure: gene->mRNA->CDS')

    # trfBig simple repeats (BED 4+12)
    parser.add_argument('--bedSimpleRepeats', action='append', help='BED 4+12 format, using simpleRepeats.as')

    # regtools (BED 12+1)
    parser.add_argument('--bedSpliceJunctions', action='append', help='BED 12+1 format, using spliceJunctions.as')

    # tblastn alignment (blastxml)
    parser.add_argument('--blastxml', action='append', help='blastxml format from tblastn')

    # BAM format
    parser.add_argument('--bam', action='append', help='BAM format from HISAT')
    # put bam index file at the same directory with bam file
    parser.add_argument('--bai', action='append', help='BAM index format from HISAT') 

    # BIGWIG format
    parser.add_argument('--bigwig', action='append', help='BIGWIG format to show rnaseq coverage')

    # GTF format
    parser.add_argument('--gtf', action='append', help='GTF format from StringTie')

    args = parser.parse_args()
    all_datatype_dictionary = dict()
    

    reference = args.fasta
    genome = 'unknown'
    out_path = '.'
    extra_files_path = '.'
    if args.genome_name:
        genome = utils.sanitize_name_path(args.genome_name)
    if args.out:
        out_path = args.out
    if args.extra_files_path:
        extra_files_path = utils.sanitize_name_path(args.extra_files_path)
    cwd = os.getcwd()
    #tool_directory not work for Galaxy tool, all tools need to exist in the current PATH, deal with it with tool dependencies
    tool_directory = os.path.join(cwd, 'JBrowse-1.12.1/bin')
    chrom_size = utils.getChromSizes(reference, tool_directory)
    all_tracks = trackObject.trackObject(chrom_size.name, genome, extra_files_path) #store converted files in the array: all_tracks.tracks
    array_inputs_bam = args.bam
    array_inputs_bai = args.bai
    array_inputs_bed_simple_repeats = args.bedSimpleRepeats
    array_inputs_bed_splice_junctions = args.bedSpliceJunctions
    array_inputs_bigwig = args.bigwig
    array_inputs_gff3_transcript = args.gff3_transcript
    array_inputs_gff3_mrna = args.gff3_mrna
    array_inputs_gtf = args.gtf
    array_inputs_blastxml = args.blastxml
    if array_inputs_bam:
        all_datatype_dictionary['bam'] = array_inputs_bam
    if array_inputs_bai:
        all_datatype_dictionary['bai'] = array_inputs_bai
    if array_inputs_bed_simple_repeats:
        all_datatype_dictionary['bedSimpleRepeats'] = array_inputs_bed_simple_repeats
    if array_inputs_bed_splice_junctions:
        all_datatype_dictionary['bedSpliceJunctions'] = array_inputs_bed_splice_junctions
    if array_inputs_bigwig:
        all_datatype_dictionary['bigwig'] = array_inputs_bigwig
    if array_inputs_gff3_transcript:
        all_datatype_dictionary['gff3_transcript'] = array_inputs_gff3_transcript
    if array_inputs_gff3_mrna:
        all_datatype_dictionary['gff3_mrna'] = array_inputs_gff3_mrna
    if array_inputs_gtf:
        all_datatype_dictionary['gtf'] = array_inputs_gtf
    if array_inputs_blastxml:
        all_datatype_dictionary['blastxml'] = array_inputs_blastxml
    
    print all_datatype_dictionary

    for datatype, inputfiles in all_datatype_dictionary.items():
        try:
            if not inputfiles:
                raise ValueError('empty input, must provide track files!\n')
        except IOError:
            print 'Cannot open', datatype
        else:
            for f in inputfiles:
                all_tracks.addToRaw(f, datatype)

    jbrowseHub = TrackHub.TrackHub(all_tracks, reference, out_path, tool_directory, genome, extra_files_path)
    jbrowseHub.createHub()
         
    

'''
    if reference:
        p = subprocess.Popen(['JBrowse-1.12.1/bin/prepare-refseqs.pl', '--fasta', reference, '--out', out_path])
        # Wait for process to terminate.
        p.communicate()
    else:
        parser.print_help()

   
    if input_simple_repeats:
        bedToGff3(input_simple_repeats, chrom_size, 'trfbig', 'repeats.gff3')
        label = "repeats"
        p = subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'repeats.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
        p.communicate()
    if input_splice_junctions:
        bedToGff3(input_splice_junctions, chrom_size, 'regtools', 'regtools.gff3')
        label = "regtools"
        p = subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'regtools.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
        p.communicate()
        attr = dict()
        track = dict()
        attr['glyph'] = 'JBrowse/View/FeatureGlyph/Segments'
        track['regtools'] = attr
        json_file = os.path.join(out_path, "trackList.json")
        utils.add_tracks_to_json(json_file, track, 'add_attr')
    if blastxml:
        blastxmlToGff3.blastxml2gff3(blastxml, "blast.gff3")
        label = "blast"
        p = subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'blast.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
        p.communicate()
    if array_inputs_gff3:
        for gff3 in array_inputs_gff3:
            label = os.path.basename(gff3)
            label = label.replace('.', '_')
            p = subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', gff3, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
            p.communicate()
            if 'Augustus' in label:
                attr = dict()
                track = dict()
                attr['transcriptType'] = 'transcript'
                track['Augustus'] = attr
                json_file = os.path.join(out_path, "trackList.json")
                utils.add_tracks_to_json(json_file, track, 'add_attr')
    if bam:
        json_file = os.path.join(out_path, "trackList.json")
        bam_track = dict()
        bam_track['type'] = 'JBrowse/View/Track/Alignments2'
        bam_track['label'] = 'alignments'
        bam_track['urlTemplate'] = '../raw/HISAT_on_data_3,_data_2,_and_data_1.bam'
        utils.add_tracks_to_json(json_file, bam_track, 'add_tracks')
        print "add bam track\n"
    if bigwig:
        json_file = os.path.join(out_path, "trackList.json")
        bigwig_track = dict()
        bigwig_track['label'] = 'rnaseq'
        bigwig_track['key'] = 'RNA-Seq Coverage'
        bigwig_track['urlTemplate'] = '../raw/Convert_Bam_to_BigWig_on_data_3_and_data_15.bigwig'
        bigwig_track['type'] = 'JBrowse/View/Track/Wiggle/XYPlot'
        bigwig_track['variance_band'] = True
        bigwig_track['style'] = dict()
        bigwig_track['style']['pos_color'] = '#FFA600'
        bigwig_track['style']['neg_color'] = '#005EFF'
        bigwig_track['style']['clip_marker_color'] = 'red'
        bigwig_track['style']['height'] = 100
        utils.add_tracks_to_json(json_file, bigwig_track, 'add_tracks')
    
    if gtf:
        utils.gtfToGff3(gtf, 'stringtie.gff3', chrom_size)
        label = os.path.basename('stringtie')
        p = subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'stringtie.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
        p.communicate()
        attr = dict()
        track = dict()
        attr['glyph'] = 'JBrowse/View/FeatureGlyph/Segments'
        track['stringtie'] = attr
        json_file = os.path.join(out_path, "trackList.json")
        utils.add_tracks_to_json(json_file, track, 'add_attr')
        
    # Index name, it takes a long time, exclude it for now
    p = subprocess.Popen(['JBrowse-1.12.1/bin/generate-names.pl', '-v', '--out', out_path])
    p.communicate()
    print "finished name index \n"
'''

if __name__ == "__main__":
    main(sys.argv)

