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
import sys
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

    def __init__(self, path, level=logging.DEBUG, print_level=logging.INFO):
        
        self.level = level
        self.print_level = print_level
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
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

            # Assign stdout handler
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(self.print_level)
            stdout_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
            stdout_handler.setFormatter(stdout_formatter)

            self.logger.addHandler(stdout_handler)

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
        logger.info("Starting package installation [%s]", self.name)
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

class ThalassaApiInstaller():
    """ Installs ThalassaApi """

    @staticmethod
    def are_requirements_met():
        """ Cheks requirements for Thalassa API """

        logger.info("Checking requirements for ThalassaApiIstaller...")
        logger.info("Everything is OK.")
        return True

    def install(self, *, install_path, sources_path, user):
        """ Instal Thalassa Api from given sources in path specified
            in instal_path. Set files and dirs for user. """
        
        logger.info("Starting Thalassa Api installation...")
        # Remove old installation if one exists
        if os.path.exists(install_path):
            shutil.rmtree(install_path, ignore_errors=True)
            logger.info("Old installation was removed")

        shutil.copytree(sources_path, install_path)
        logger.debug("All files copied.")

        for root, dirs, files in os.walk(install_path):
            for dir in dirs:
                shutil.chown(os.path.join(root, dir), user)
            for file in files:
                shutil.chown(os.path.join(root, file), user)
        logger.debug("Files and directories owner updated to: [%s]", user)

        logger.info("Thalassa Api was installed.")
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
        ThalassaApiInstaller.are_requirements_met(),
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
    thalassa_api = ThalassaApiInstaller()
    was_installed = thalassa_api.install(install_path=config["thalassa_path"]["api"],
                                         sources_path="%s/ThalassaApi" % config["sources"],
                                         user=config["user"])
    if not was_installed:
        print("Warning: Thalassa Api was not installed")
