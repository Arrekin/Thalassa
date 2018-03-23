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
    parser.add_argument("--stdout_level",
                        help="Set logs level that should be printed to stdout(default INFO)",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        action='store')
    parser.add_argument("--log_level",
                        help="Set logs level for logs stored in files(default DEBUG)",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='DEBUG',
                        action='store')
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
    """ Mark installation as failure and exit installator. """
    logger.error("Installation failed :<")
    print("Installation failed, check logs.")
    exit()


def ensure_path_exists(path, user=None):
    """ Checks whether given path exists and create it if not.
        If user is specified he will take ownership of deepest catalog. """
    if not path:
        return

    path_parts = path.split('/')

    # Check if path is absolute or relative
    path_to_check = "/" if path[0] == '/' else ''
    for path_part in path_parts:
        path_to_check = path_to_check + path_part
        if not os.path.isdir(path_to_check):
            os.mkdir(path_to_check)
        path_to_check = path_to_check + "/"

    if user is not None:
        # Chown final directory(-1 to remove trailing slash)
        shutil.chown(path_to_check[:-1], user)


class InstallerLogger:
    """ Logging wrapper for this installer. """

    __loggers = {}
    __levels_mapper = {
            'DEBUG': logging.DEBUG,
            'INFO' : logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

    def __init__(self, path, *, logfile_level='DEBUG', stdout_level='INFO'):
        self.logfile_level = self.__class__.__levels_mapper[logfile_level]
        self.stdout_level = self.__class__.__levels_mapper[stdout_level]
        self.level = min(self.logfile_level, self.stdout_level)
        try:
            self.logger = InstallerLogger.__loggers[__name__]
        except KeyError:
            # Get logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(self.level)

            # Assign file handler
            logfilename = "%s/ThalassaInstaller-%s.log" % (path, str(time.time()))
            handler = logging.FileHandler(logfilename)
            handler.setLevel(self.logfile_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

            # Assign stdout handler
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(self.stdout_level)
            stdout_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
            stdout_handler.setFormatter(stdout_formatter)

            self.logger.addHandler(stdout_handler)

            # Add logger to the dict so we do not need to setup it anymore
            self.__class__.__loggers[__name__] = self.logger

    def debug(self, *args, **kwargs):
        """ Wrapper for logging.debug """
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """ Wrapper for logging.info """
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """ Wrapper for logging.warning """
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """ Wrapper for logging.error """
        self.logger.error(*args, **kwargs)


class Pip3Installer:
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
            logger.error("python3-pip is not installed! Terminating installation...")
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


class AptInstaller:
    """ Handles installation of 3rd party packages via apt-get. """

    @staticmethod
    def are_requirements_met():
        """ Cheks requirements for python packages installer """

        logger.info("Checking requirements for AptInstaller...") 
        logger.info("Everything is OK.")
        return True

    def __init__(self, name):
        """ 
            - name - 3rd party package name
        """
        self.name = name

    def install(self, *,
                force_reinstall=False # If true package will be reinstalled
                ):
        logger.info("Starting package installation [%s]", self.name)
        package_already_exists = False
        # First check whether package is already installed
        bash_cmd = "dpkg -l | grep \'\\b\'%s | wc -l" % self.name
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
        
        bash_cmd = "apt-get install %s %s" % (
            "--reinstall" if force_reinstall and package_already_exists else "",
            self.name)
        out, err = execute_bash_command(bash_cmd, shell=True)
        if err:
            logger.error("Unexpected error when installing 3rd party package [%s]", 
                         self.name)
            return False

        logger.info("Package [%s] was installed.", self.name)
        return True


class CopyInstaller():
    """ Installs by just copying files """

    @staticmethod
    def are_requirements_met():
        """ Cheks requirements for CopyInstaller """

        logger.info("Checking requirements for CopyIstaller...")
        logger.info("Everything is OK.")
        return True

    def __init__(self, *, name):
        """ 
        Keyword arguments:
        name         -- what is being installed
        """
        self.name = name

    def install(self, *, install_path, sources_path, user):
        """ Install package.
        Keyword arguments:
        name         -- what is being installed
        install_path -- where to copy files(i.e. installation directory)
        sources_path -- catalog to be copied to install_path
        user         -- installation catalog and all its nodes are to be owned by this guy
        """
        logger.info("Starting {name} installation...".format(name=self.name))
        # Remove old installation if one exists
        if os.path.exists(install_path):
            shutil.rmtree(install_path, ignore_errors=True)
            logger.info("Old installation was removed")
        else:
            # Ensure that path exists but remove final catalog so copytree wont fail
            ensure_path_exists(install_path)
            os.rmdir(install_path)

        shutil.copytree(sources_path, install_path)
        logger.debug("All files copied.")

        # Ensure that all files belong to specified user
        for root, dirs, files in os.walk(install_path):
            for dir in dirs:
                shutil.chown(os.path.join(root, dir), user)
            for file in files:
                shutil.chown(os.path.join(root, file), user)
        logger.debug("Files and directories owner updated to: [%s]", user)

        logger.info("{name} was installed.".format(name=self.name))
        return True


def install_sqlite():
    """ Install sqlite3. """
    sqlite = AptInstaller("sqlite3")
    was_installed = sqlite.install(force_reinstall=False)
    if not was_installed:
        print("Warning: sqlite3 was not installed")

    libsqlite = AptInstaller("libsqlite3-dev")
    was_installed = libsqlite.install(force_reinstall=False)
    if not was_installed:
        print("Warning: libsqlite3-dev was not installed")


def install_beanstalkd():
    """ Install beanstalkd. """
    beanstalk = AptInstaller("beanstalkd")
    was_installed = beanstalk.install(force_reinstall=False)
    if not was_installed:
        print("Warning: beanstalkd was not installed")


def initialize_database(*, config_path):
    """ Sets up things for database.
    Keyword arguments:
    config_path -- catalog containing database config
    """
    logger.info("Starting database initialization...")
    try:
        config_filepath = "{}/database_config.yaml".format(config_path)
        with open(config_filepath, 'r') as conf_file:
            config = yaml.load(conf_file)
    except IOError as exception:
        logger.error("Failed to load database configuration!", exc_info=True)
        fail_installation()
    # DB destination
    db_store_path = config['db_store_path']
    ensure_path_exists(db_store_path, user=config['user'])
    logger.debug("Databse store catalog set to: [{}]".format(db_store_path))
    logger.info("Database was initialized.")


def install_ThalassaCore(*, sources_path):
    """ Installs ThalassaCore from sources.
    Keyword arguments:
    sources_path -- path to main Thalassa sources catalog
    """
    package_path = "{}/ThalassaCore".format(sources_path)
    thalassa_core = Pip3Installer("Thalassa")
    was_installed = thalassa_core.install(force_reinstall=True,
                                          install_dependencies=False,
                                          package_path=package_path)
    if not was_installed:
        print("Warning: Thalassa Core was not installed")


def install_ThalassaApi(*, install_path, sources_path, user):
    """ Installs ThalassaApi from given sources.
    Keyword arguments:
    install_path -- path to where ThalasaApi should be installed
    sources_path -- path to main Thalassa sources catalog
    user         -- user to own installation
    """
    package_path = "{}/ThalassaApi".format(sources_path)
    thalassa_api = CopyInstaller(name="Thalassa Api")
    was_installed = thalassa_api.install(install_path=install_path,
                                         sources_path=package_path,
                                         user=user)
    if not was_installed:
        print("Warning: Thalassa Api was not installed")


def install_ThalassaConfig(*, install_path, sources_path, user):
    """ Copy configuration files to install destination.
    Keyword arguments:
    install_path -- where to store configuration
    sources_path -- path to main Thalassa sources catalog
    user         -- user to own configuration catalog and files
    """
    package_path = "{}/ThalassaConfig".format(sources_path)
    thalassa_config = CopyInstaller(name="Thalassa Config")
    was_installed = thalassa_config.install(install_path=install_path,
                                            sources_path=package_path,
                                            user=user)
    if not was_installed:
        print("Warning: Thalassa Api was not installed")



if __name__ == "__main__":
    args = parse_arguments()

    # First initialize installator logger
    logging_dir = "/var/log/ThalassaInstall"
    ensure_path_exists(logging_dir)

    logger = InstallerLogger(logging_dir,
                             logfile_level=args.log_level,
                             stdout_level=args.stdout_level)

    logger.info("Installer started.")

    # Now check wheter installer has all it needs.
    logger.info("Evaluating installation requirements...")
    evaluation_table = [
        Pip3Installer.are_requirements_met(),
        CopyInstaller.are_requirements_met(),
    ]

    if not all(evaluation_table):
        fail_installation()

    # Load configuration file
    try:
        with open(args.conf, 'r') as conf_file:
            config = yaml.load(conf_file)
    except IOError as exception:
        logger.error("Failed to load configuration!", exc_info=True)
        fail_installation()

    logger.info("Configuration loaded.")
    logger.debug(config)

    # Ensure logging path exists
    ensure_path_exists(config['thalassa_path']['logs'], user=config['user'])
    logger.info("Path for logs created: [{}]".format(config['thalassa_path']['logs']))

    install_sqlite()
    install_beanstalkd()

    install_ThalassaCore(sources_path=config["sources"])

    install_ThalassaConfig(install_path=config["thalassa_path"]["config"],
                           sources_path=config["sources"],
                           user=config["user"])

    install_ThalassaApi(install_path=config["thalassa_path"]["api"],
                        sources_path=config["sources"],
                        user=config["user"])

    initialize_database(config_path=config["thalassa_path"]["config"])
