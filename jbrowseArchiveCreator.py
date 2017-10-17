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
    apollo_path = reader.getApolloPath()
    apollo_host = reader.getApolloHost()
    apollo_user = reader.getApolloUser()
 
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
    trackHub = TrackHub(reference_genome, apollo_user, outputFile, extra_files_path, toolDirectory, track_type, apollo_host, user_email) 

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