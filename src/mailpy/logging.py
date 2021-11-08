import logging
import logging.config
import os

import yaml

LOGGING_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logging.yml",
)

if not os.path.exists(LOGGING_CONFIG_PATH):
    raise ValueError(f"Falid to load logging settings from file {LOGGING_CONFIG_PATH}")

with open(LOGGING_CONFIG_PATH, "r") as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)


def getLogger(name=None):
    return logging.getLogger(name)
