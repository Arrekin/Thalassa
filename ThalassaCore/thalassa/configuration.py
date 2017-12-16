""" This module holds are configuration data. """
import logging
import yaml


class LoggingConfig:
    """ Proxy to access logging configuration. """
    
    # Reference to actual config
    __config = None
    # Filepath to file from which config can be loaded
    __yaml_filepath = "/etc/thalassa/logging_config.yaml"

    def __init__(self):
        # Create config if it were not loaded yet.
        if not self.__class__.__config:
            new_config = _Config()
            new_config.load_from_yaml(yaml_filepath=self.__class__.__yaml_filepath)
            self.__class__.__config = new_config

    def as_dict(self):
        """ Return configuration as dict object. """
        return self.__class__.__config

    def __getattr__(self, name):
        return __config[name]



# Private area
class _Config(dict):
    """ Stores configuration accessible as class attributes. """

    def load_from_yaml(self, yaml_filepath, erase_current=True):
        """ Loads yaml file. 
        
        Keyword arguments:
        yaml_filepath -- path to file on disk containing valid yaml file
        erase_current -- whether to delete current config or to just update
        """

        with open(yaml_filepath, 'r') as file_stream:
            new_config = yaml.load(file_stream)
            if erase_current:
                self.clear()
            self.update(new_config)


    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("No such attribiute: " + name)


    def __setattr__(self, name, value):
        self[name] = value


    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError("No such attribiute: " + name)