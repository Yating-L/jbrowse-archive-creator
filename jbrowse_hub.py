#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from bedToGff3 import bedToGff3
import blastxmlToGff3

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

    args = parser.parse_args()

    reference = args.fasta
    out_path = args.out
    array_inputs_gff3 = args.gff3
    input_simple_repeats = args.bedSimpleRepeats
    input_splice_junctions = args.bedSpliceJunctions
    chrom_size = args.chromsize
    blastxml = args.blastxml

    subprocess.Popen(['JBrowse-1.12.1/bin/prepare-refseqs.pl', '--fasta', reference, '--out', out_path])
    if input_simple_repeats:
        bedToGff3(input_simple_repeats, chrom_size, 'trfbig', 'repeats.gff3')
        label = "repeats"
        subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'repeats.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
    if input_splice_junctions:
        bedToGff3(input_splice_junctions, chrom_size, 'regtools', 'regtools.gff3')
        label = "regtools"
        subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'regtools.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
    if blastxml:
        blastxmlToGff3.blastxml2gff3(blastxml, "blast.gff3")
        label = "blast"
        subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', 'blast.gff3', '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
    if array_inputs_gff3:
        for gff3 in array_inputs_gff3:
            label = os.path.basename(gff3)
            label = label.replace('.', '_')
            print label
            subprocess.Popen(['JBrowse-1.12.1/bin/flatfile-to-json.pl', '--gff', gff3, '--trackType', 'CanvasFeatures', '--trackLabel', label, '--out', out_path])
    
    subprocess.Popen(['JBrowse-1.12.1/bin/generate-names.pl', '-v', '--out', out_path])

if __name__ == "__main__":
    main(sys.argv)

