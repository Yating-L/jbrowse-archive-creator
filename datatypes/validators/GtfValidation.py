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
import re

from DataValidation import DataValidation


class GtfValidation(DataValidation):
    
    def __init__(self, inputFile, fileType, chromSizesFile, options=None):
        super(GtfValidation, self).__init__(inputFile, fileType, chromSizesFile, options)
    
    def validate(self):
        """validate input file format"""
        self._checkAndFixGtf()
        if self.is_modified:
            print("- Warning: Gtf created with a modified version of your Gtf because of start/end coordinates issues.")
            print("Here are the lines removed: " + self._get_str_modified_lines())
        return self.inputFile
    
                
        
    def _checkAndFixGtf(self):
        """
        Call _checkAndFixGtf, check the integrity of gtf file, 
        if coordinates exceed chromosome size, either removed the whole line(s) or truncated to the end of the scaffold 
        depending on the user choice
        default: remove the whole line(s)
        """
        # Set the boolean telling if we had to modify the file
        self.is_modified = False
        self.array_modified_lines = []
        # Create a temp gtf just in case we have issues
        temp_gtf = tempfile.NamedTemporaryFile(bufsize=0, suffix=".gtf", delete=False)

        # TODO: Get the user choice and use it
        # TODO: Check if the start > 0 and the end <= chromosome size
        # Get the chrom.sizes into a dictionary to have a faster access
        # TODO: Think about doing this in Datatype.py, so everywhere we have access to this read-only dictionary
        dict_chrom_sizes = {}
        with open(self.chromSizesFile, 'r') as chromSizes:
            lines = chromSizes.readlines()
            for line in lines:
                fields = line.split()
                # fields[1] should be the name of the scaffold
                # fields[2] should be the size of the scaffold
                # TODO: Ensure this is true for all lines
                dict_chrom_sizes[fields[0]] = fields[1]

        # Parse the GTF and check each line using the chrom sizes dictionary
        with open(temp_gtf.name, 'a+') as tmp:
            with open(self.inputFile, 'r') as gtf:
                lines = gtf.readlines()
                for index, line in enumerate(lines):
                    # If this is not a comment, we check the fields
                    if not line.startswith('#'):
                        fields = line.split()
                        # We are interested in fields[0] => Seqname (scaffold)
                        # We are interested in fields[3] => Start of the scaffold
                        # We are interested in fields[4] => End of the scaffold
                        scaffold_size = dict_chrom_sizes[fields[0]]
                        start_position = fields[3]
                        end_position = fields[4]

                        if start_position > 0 and end_position <= scaffold_size:
                            # We are good, so we copy this line
                            tmp.write(line)
                            tmp.write(os.linesep)


                        # The sequence is not good, we are going to process it regarding the user choice
                        # TODO: Process the user choice
                        # By default, we are assuming the user choice is to remove the lines: We don't copy it

                        # If we are here, it means the gtf has been modified
                        else:
                            # We save the line for the feedback to the user
                            self.array_modified_lines.append(index + 1)

                            if self.is_modified is False:
                                self.is_modified = True
                            else:
                                pass
                    else:
                        tmp.write(line)
                        tmp.write(os.linesep)

        # Once the process it completed, we just replace the path of the gtf
        self.inputFile = temp_gtf.name

        # TODO: Manage the issue with the fact the dataset is going to still exist on the disk because of delete=False
        #return modified_gtf
    
    def _get_str_modified_lines(self):
        return ','.join(map(str, self.array_modified_lines))
                    