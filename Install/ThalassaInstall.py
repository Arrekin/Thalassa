"""
------------------------------
-Thalassa Installator script.-
------------------------------

Requieres Python3 and pip3.
"""
import argparse
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