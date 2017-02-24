#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from bedToGff3 import bedToGff3
import blastxmlToGff3
import utils
import tempfile

def main(argv):
    parser = argparse.ArgumentParser(description='Create a hub to display in jbrowse.')

    # Reference genome mandatory
    parser.add_argument('-f', '--fasta', help='Fasta file of the reference genome')

    # Output folder
    parser.add_argument('-o', '--out', help='Output directory')

    # GFF3
    parser.add_argument('--gff3', action='append', help='GFF3 format')

    # trfBig simple repeats (BED 4+12)
    parser.add_argument('--bedSimpleRepeats', help='BED 4+12 format, using simpleRepeats.as')

    # regtools (BED 12+1)
    parser.add_argument('--bedSpliceJunctions', help='BED 12+1 format, using spliceJunctions.as')

    # tblastn alignment (blastxml)
    parser.add_argument('--blastxml', help='blastxml format from tblastn')

    # chromsize file (tab)
    parser.add_argument('--chromsize', help='Chrome size file')

    # BAM format
    parser.add_argument('--bam', help='BAM format from HISAT')

    # BIGWIG format
    parser.add_argument('--bigwig', help='BIGWIG format to show rnaseq coverage')

    args = parser.parse_args()

    reference = args.fasta
    out_path = args.out
    array_inputs_gff3 = args.gff3
    input_simple_repeats = args.bedSimpleRepeats
    input_splice_junctions = args.bedSpliceJunctions
    chrom_size = args.chromsize
    blastxml = args.blastxml
    bam = args.bam
    bigwig = args.bigwig

    if reference:
        p = subprocess.Popen(['JBrowse-1.12.1/bin/prepare-refseqs.pl', '--fasta', reference, '--out', out_path])
        # Wait for process to terminate.
        p.communicate()
    else:
        print "No genome reference \n"
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
        
    # Index name, it takes a long time, exclude it for now
    p = subprocess.Popen(['JBrowse-1.12.1/bin/generate-names.pl', '-v', '--out', out_path])
    p.communicate()
    print "finished name index \n"

if __name__ == "__main__":
    main(sys.argv)

