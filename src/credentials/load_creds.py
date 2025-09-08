import logging
import os
import sys

import yaml

from models.creds.creds_file import CredsFile


def load_credentials_file(i_cred_file: str | None = None) -> CredsFile:
    """Loads a single credentials file and returns its contents as a CredsFile object.

    This function processes a provided YAML file containing credential data. It checks
    the existence of the file, reads its content, and converts the data into
    a CredsFile object for further use. If the file does not exist, the program
    logs an error and exits.

    Args:
        i_cred_file (str, optional): Path to the credentials file. Defaults to None.

    Returns:
        CredsFile: An instance of CredsFile populated with the credentials
        data from the provided file.

    Raises:
        SystemExit: If the specified credentials file does not exist.
    """
    # Load single credential file if specified
    if not os.path.exists(i_cred_file):
        logging.error(f"Credentials file not found: {i_cred_file}")
        sys.exit(1)

    with open(i_cred_file, encoding="utf-8") as f:
        d_creds = yaml.safe_load(f)
        creds_file = CredsFile(**d_creds)
        return creds_file


def load_credentials_folder(i_cred_folder: str | None = None) -> CredsFile:
    """Load and merge all YAML files from a specified credentials folder.

    This function iterates through the specified credentials folder, reads all
    the YAML files present in it, and merges their contents into a single
    CredsFile object. It assumes that the folder exists and each YAML file
    adheres to the structure expected by the CredsFile class.

    Args:
        i_cred_folder (str, optional): The path to the folder containing credentials
            YAML files. If None, the function will fail to operate properly.

    Returns:
        CredsFile: An aggregated CredsFile object containing merged data from all
        the processed YAML files.

    Raises:
        SystemExit: If the specified folder does not exist or is not found.
    """
    # Load and merge all yaml files from credentials folder if specified
    if not os.path.exists(i_cred_folder):
        logging.error(f"Credentials folder not found: {i_cred_folder}")
        sys.exit(1)

    creds_file = CredsFile()
    for filename in os.listdir(i_cred_folder):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(i_cred_folder, filename)
            with open(file_path, encoding="utf-8") as f:
                d_creds = yaml.safe_load(f)
                local_creds_file = CredsFile(**d_creds)
                creds_file.image.extend(local_creds_file.image)
                creds_file.helm.extend(local_creds_file.helm)
                creds_file.git.extend(local_creds_file.git)
                creds_file.scanners.extend(local_creds_file.scanners)
    return creds_file
