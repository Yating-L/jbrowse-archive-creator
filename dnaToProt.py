#!/usr/bin/env python

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

def dnaToProt(dna_seq):
    coding_seq = Seq(dna_seq, IUPAC.unambiguous_dna)
    return coding_seq.translate()

def addProtToMenu(json_file, track):
    trackAttr = dict()
    menu_item = dict()
    menu_item2 = dict()
    menu_item3 = dict()
    trackAttr['menuTemplate'] = []
    menu_item['label'] = 'View details'
    menu_item2['label'] = 'Highlight this gene'
    menu_item3['label'] = 'View translated protein'
    menu_item3['iconClass'] = 'dijitIconDatabase'
    menu_item3['action'] = 'contentDialog'
    menu_item3['content'] = "function(track,feature) { var sub = feature.get('subfeatures') return '<h2>{name}</h2><p>Subfeatures: feature.get('name')</p>';}"
    trackAttr['menuTemplate'].append(menu_item, menu_item2, menu_item3)
    
