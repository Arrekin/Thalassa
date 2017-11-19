"""
------------------------------
-Thalassa Installator script.-
------------------------------

Requieres Python3 and pip3.
"""
import argparse
import os
import shutil
import subprocess
import yaml

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf",
                        help="Allows to provide custom configuration",
                        default="configuration.yaml")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Load configuration file
    try:
        with open(args.conf, 'r') as conf_file:
            config = yaml.load(conf_file)
    except IOError as exception:
        print("Failed to load configuration")
        print(exception)
        exit()

    print(config)

    # Install ThalassaCore
    bash_command = "pip3 install --ignore-installed %s/ThalassaCore" % config["sources"]
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    print(out)
    print(err)

    # Install ThalassaAPI service
    api_path = config["thalassa_path"]
    if not os.path.isdir(api_path):
        os.mkdir(api_path)
        shutil.chown(api_path, user=config["user"])
    shutil.copy("%s/ThalassaApi/ThalassaApi.py" % config["sources"], "%s/ThalassaApi.py" % config["thalassa_path"])
    shutil.chown("%s/ThalassaApi.py" % config["thalassa_path"], user=config["user"])
