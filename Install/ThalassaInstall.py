"""
------------------------------
-Thalassa Installator script.-
------------------------------

Requieres Python3 and pip3.
"""
import argparse
import logging
import os
import shutil
import subprocess
import time
import yaml


def parse_arguments():
    """ Parses command line arguments. """

    parser = argparse.ArgumentParser()
    parser.add_argument("--conf",
                        help="Allows to provide custom configuration",
                        default="configuration.yaml")
    return parser.parse_args()


def execute_bash_command(command, shell=False):
    """ Executes given bash command. """

    logger.debug("Running bash command [%s]", command)
    command = command if shell else command.split()
    process = subprocess.Popen(command, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=shell)
    out, err = process.communicate()

    if out:
        logger.debug("The command stdout: %s", out)
    if err:
        logger.error("The command stderr: %s", err)

    return out, err

def fail_installation():
    logger.error("Installation failed :<")
    print("Installation failed, check logs.")
    exit()

class InstallerLogger():
    """ Logging wrapper for this installer. """

    __loggers = {}

    def __init__(self, path, level=logging.DEBUG):
        
        self.level = level
        try:
            self.logger = InstallerLogger.__loggers[__name__]
        except KeyError:
            # Get logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(self.level)

            # Assign file handler
            logfilename = "%s/ThalassaInstaller-%s.log" % (path, str(time.time()))
            handler = logging.FileHandler(logfilename)
            handler.setLevel(self.level)

            # Assign formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

            # Add logger to the dict so we do not need to setup it anymore
            InstallerLogger.__loggers[__name__] = self.logger

    def debug(self, *args):
        """ Wrapper for logging.debug """

        self.logger.debug(*args)

    def info(self, *args):
        """ Wrapper for logging.info """

        self.logger.info(*args)

    def warning(self, *args):
        """ Wrapper for logging.warning """

        self.logger.warning(*args)

    def error(self, *args):
        """ Wrapper for logging.error """

        self.logger.error(*args)


class Pip3Installer():
    """ Handles installation of python packages via pip3. """

    @staticmethod
    def are_requirements_met():
        """ Cheks requirements for python packages installer """

        logger.info("Checking requirements for Pip3Installer...")
        # Check if pip3 is installed
        bash_cmd = "dpkg -l | grep python3-pip | wc -l"
        out, err = execute_bash_command(bash_cmd, shell=True)
        if err:
            logger.error("Unexpected error; Terminating installation...")
            return False
        if out != b'1\n':
            print("python3-pip is not installed!")
            logger.error("Expected command output was: 1; Terminating installation...")
            return False
        
        logger.info("Everything is OK.")
        return True

    def __init__(self, name):
        """ 
            - name - Python package name
        """

        self.name = name

    def install(self, *,
                force_reinstall=False, # If true package will be reinstalled
                install_dependencies=True, # Whether install or not dependencies
                package_path=None # Path to sources if not downloadable
                ):
        logger.info("Begin package installation [%s]", self.name)
        package_already_exists = False
        # First check whether package is already installed
        bash_cmd = "pip3 list --format=columns | grep %s | wc -l" % self.name
        out, err = execute_bash_command(bash_cmd, shell=True)
        if err:
            logger.error("Unexpected error when installing python package [%s]",
                         self.name)
            return False
        if out != b'0\n':
            package_already_exists = True
            logger.info("Package [%s] is already installed", self.name)
            if not force_reinstall:
                logger.info("[%s] package installation skipped", self.name)
                return False
        
        bash_cmd = "pip3 install %s %s %s" % (
            "--ignore-installed" if force_reinstall and package_already_exists else "",
            "--no-deps" if not install_dependencies else "",
            package_path if package_path else self.name)
        out, err = execute_bash_command(bash_cmd, shell=True)
        if err:
            logger.error("Unexpected error when installing python package [%s]", 
                         self.name)
            return False

        logger.info("Package [%s] was installed.", self.name)
        return True

if __name__ == "__main__":
    # First initialize logger
    logging_dir = "/var/log/Thalassa"
    if not os.path.isdir(logging_dir):
        os.mkdir(logging_dir)
    logger = InstallerLogger(logging_dir)

    logger.info("Installer started.")

    # Now check wheter installer has all it needs.
    logger.info("Evaluating installation requirements...")
    evaluation_table = [
        Pip3Installer.are_requirements_met(),    
    ]

    if not all(evaluation_table):
        fail_installation()

    args = parse_arguments()

    # Load configuration file
    try:
        with open(args.conf, 'r') as conf_file:
            config = yaml.load(conf_file)
    except IOError as exception:
        print("Failed to load configuration")
        logger.error("Failed to load configuration!", exc_info=True)
        fail_installation()

    logger.info("Configuration loaded.")
    logger.debug(config)

    # Install ThalassaCore
    thalassa_core = Pip3Installer("Thalassa")
    was_installed = thalassa_core.install(force_reinstall=True,
                                          install_dependencies=False,
                                          package_path="%s/ThalassaCore" % config["sources"])
    if not was_installed:
        print("Warning: Thalassa Core was not installed")


    # Install ThalassaAPI service
    api_path = config["thalassa_path"]
    if not os.path.isdir(api_path):
        os.mkdir(api_path)
        shutil.chown(api_path, user=config["user"])
    shutil.copy("%s/ThalassaApi/ThalassaApi.py" % config["sources"], "%s/ThalassaApi.py" % config["thalassa_path"])
    shutil.chown("%s/ThalassaApi.py" % config["thalassa_path"], user=config["user"])

    shutil.rmtree("%s/html" % config["thalassa_path"], ignore_errors=True)
    shutil.copytree("%s/ThalassaApi/html" % config["sources"], "%s/html" % config["thalassa_path"])
