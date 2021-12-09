import logging
import logging.config
import os

import yaml


def load_config_console():
    configfile_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "logging-console.yml",
    )
    load_config(configfile_path)


def load_config_rotating_file():
    configfile_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "logging.yml",
    )
    load_config(configfile_path)


def load_config(configfile: str):
    if configfile is None or not configfile:
        raise ValueError(f"Config file cannot be empty {configfile}")

    if not os.path.exists(configfile):
        raise ValueError(f"Falid to load logging settings from file {configfile}")

    with open(configfile, "r") as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)


def getLogger(name=None):
    return logging.getLogger(name)
