import logging
import logging.config
import os

import yaml


def load_config(configfile: str = "logging-console.yml"):
    configfile_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        configfile,
    )

    if not os.path.exists(configfile_path):
        raise ValueError(f"Falid to load logging settings from file {configfile_path}")

    with open(configfile_path, "r") as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)


def getLogger(name=None):
    return logging.getLogger(name)
