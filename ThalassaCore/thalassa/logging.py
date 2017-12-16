""" Wrapper for python logging module. """
import logging
import logging.config

import thalassa.configuration as configuration

def get_logger(name):
    """ Same as logging.get_logger but ensures that it is configured. """
    if not get_logger.is_initialized:
        print(configuration.LoggingConfig().as_dict())
        logging.config.dictConfig(configuration.LoggingConfig().as_dict())
        get_logger.is_initialized = True
    
    return logging.getLogger(name)
get_logger.is_initialized = False
