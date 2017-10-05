#!/usr/bin/python
# -*- coding: utf8 -*-

"""
This class handles the subprocess calls of the different tools used
in HubArchiveCreator
"""

import logging
import os
import subprocess
import sys
import string
import tempfile

    
def prefixTrackName(filename):       
    """
    santitize trackName. Because track name must begin with a letter and
    contain only the following chars: [a-zA-Z0-9_].
    See the "track" Common settings at:
    https://genome.ucsc.edu/goldenpath/help/trackDb/trackDbHub.html#bigPsl_-_Pairwise_Alignments
    skip the santitization for cytoBandIdeo track
    """
    if filename == 'cytoBandIdeo':
        return filename
    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    sanitize_name = ''.join([c if c in valid_chars else '_' for c in filename])
    sanitize_name = "gonramp_" + sanitize_name
    return sanitize_name

def sanitize_name_input(string_to_sanitize):
    """
    Sanitize the string passed in parameter by replacing '/' and ' ' by '_'

    :param string_to_sanitize:
    :return :

    :Example:

    >>> sanitize_name_input('this/is an//example')
    this_is_an__example
    """
    return string_to_sanitize \
            .replace("/", "_") \
            .replace(" ", "_")

def sanitize_name_inputs(inputs_data):
    """
    Sanitize value of the keys "name" of the dictionary passed in parameter.

    Because sometimes output from Galaxy, or even just file name, from user inputs, have spaces.
    Also, it can contain '/' character and could break the use of os.path function.

    :param inputs_data: dict[string, dict[string, string]]
    """
    for key in inputs_data:
        inputs_data[key]["name"] = sanitize_name_input(inputs_data[key]["name"])

def sanitize_group_name(group_name):
    return group_name.lower().replace(' ', '_')

def sanitize_name(input_name):
    """
    Galaxy will name all the files and dirs as *.dat, 
    the function can replace '.' to '_' for the dirs
    """
    validChars = "_-%s%s" % (string.ascii_letters, string.digits)
    sanitized_name = ''.join([c if c in validChars else '_' for c in input_name])
    return "gonramp_" + sanitized_name
