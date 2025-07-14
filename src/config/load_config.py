import logging
import os
import sys

import yaml

from models.config.config_file import ConfigFile


def load_config_file(config_file: str) -> ConfigFile:
    """
    Loads a configuration file and parses it into a ConfigFile object.

    This function opens the specified configuration file, reads its
    contents, parses them using YAML, and initializes a ConfigFile object
    from the parsed data. It logs the loading operation for reference.

    Args:
        config_file (str): The path to the configuration file to be loaded.

    Returns:
        ConfigFile: An instance of ConfigFile initialized with the data
        from the configuration file.

    Raises:
        FileNotFoundError: If the specified configuration file does not
        exist.
        yaml.YAMLError: If there is an error while parsing the YAML file.
    """
    logging.info(f"loading config file: {config_file}")
    with open(config_file, "r", encoding="utf-8") as f:
        d_config = yaml.safe_load(f)
        if not d_config:
            logging.warning("config file empty!")
            return ConfigFile()
        config_file = ConfigFile(**d_config)
        return config_file


def load_config_folder(config_folder: str) -> ConfigFile:
    """
    Loads and merges configuration files from a specified folder. This function reads
    all YAML files in a given directory, parses their content, and merges the
    data into a single ConfigFile object. If the folder does not exist, the program
    will log an error message and terminate.

    Args:
        config_folder (str): The path to the folder containing YAML configuration
            files to be loaded.

    Raises:
        Exception: If an error occurs during the loading of any YAML configuration
            file, it is re-raised after logging the error.

    Returns:
        ConfigFile: A merged configuration object containing scanners and resources
            from all valid YAML files in the specified folder.
    """
    if not os.path.exists(config_folder):
        logging.error(f"Config folder not found: {config_folder}")
        sys.exit(1)

    tmp_config = {"scanners": [], "resources": []}
    for filename in os.listdir(config_folder):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(config_folder, filename)
            logging.info(f"loading config file: {filename}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    d_local_config = yaml.safe_load(f)
                    if not d_local_config:
                        logging.warning("config file empty!")
                        continue
                    local_config_file = ConfigFile(**d_local_config)
                    tmp_config["scanners"].extend(local_config_file.scanners)
                    tmp_config["resources"].extend(local_config_file.resources)
            except Exception as e:
                logging.error(f"Error loading config file {filename}")
                raise e
    return ConfigFile(**tmp_config)
