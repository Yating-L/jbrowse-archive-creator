import os
import sys
import json
import logging
import logging.config

#from util.Filters import TraceBackFormatter

class Logger(object):
    def __init__(self, tool_directory, debug="False", extra_files_path=None):
        self.tool_directory = tool_directory
        self.default_level = logging.INFO
        self.debug = debug
        self.extra_files_path = extra_files_path

    def setup_logging(self):
        """Setup logging configuration
        reference: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
        """
        config_path = os.path.join(self.tool_directory, 'logging.json')
        default_level=logging.INFO
        if self.debug.lower() == "true":
            default_level=logging.DEBUG
        if os.path.exists(config_path):
            with open(config_path, 'rt') as f:
                config = json.load(f)
            config["handlers"]["console"]["level"] = default_level
            if self.extra_files_path:
                for i in config["handlers"]:
                    if "filename" in config["handlers"][i]:
                        config["handlers"][i]["filename"] = os.path.join(self.extra_files_path, config["handlers"][i]["filename"])
                logging.config.dictConfig(config)
            else:
                logging.warn("Extra files path is not set. The log files will exist at current working directory instead of final output folder")
        else:
            logging.basicConfig(level=default_level)
            logging.warn("Cannot find logging configuration file!\n")

