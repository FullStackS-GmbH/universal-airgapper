import logging
import os
import re
import shutil
from pathlib import Path
from typing import List

from git import GitCommandError, Repo

from models.creds.creds import Creds
from models.resources.git import GitRepo


def get_all_tags_remote(
    repo_url: str,
    target_path: str,
    username: str = None,
    password: str = None,
    ssh_key_path: str = None,
) -> List[str]:
    """
    Retrieves all tags from a remote Git repository.

    This function interacts with a remote Git repository to fetch all available tags by
    cloning the repository into a temporary directory. It supports both HTTPS and SSH
    authentication mechanisms. The temporary directory used for cloning is cleaned up
    after the operation, irrespective of its success or failure.

    Args:
        repo_url (str): The URL of the remote Git repository.
        target_path (str): The local path where the repository will be temporarily cloned.
        username (str, optional): The username for HTTPS authentication. Defaults to None.
        password (str, optional): The password for HTTPS authentication. Defaults to None.
        ssh_key_path (str, optional): The path to the SSH private key file for SSH
            authentication. Defaults to None.

    Returns:
        list[str]: A list of tag names retrieved from the remote repository. Returns an
            empty list in case of any errors during the process.
    """
    try:
        # Create target directory if it doesn't exist
        target_dir = Path(target_path)
        # Cleanup target path if requested
        shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Configure authentication
        if repo_url.startswith("git@"):  # SSH authentication
            logging.debug(f"using ssh key @ {ssh_key_path}")
            if not ssh_key_path or not os.path.exists(ssh_key_path):
                logging.error(f"no ssk key found: {ssh_key_path}")
                return []
            os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path}"
        elif username and password:  # HTTPS authentication
            # Modify the repo_url to include username and password for HTTPS if provided
            logging.debug(f"using username [{username}] and password for HTTPS auth")
            url_parts = repo_url.split("://")
            repo_url = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"
        elif username or password:
            logging.error(
                "Both username and password are required for HTTPS authentication."
            )
            return []

        # Clone the repository into the temporary directory (shallow clone --tags only)
        repo = Repo.clone_from(
            repo_url,
            target_path,
            depth=1,
            multi_options=[
                "--single-branch",
                "--no-checkout",
                "--filter=blob:none",
                "--no-tags",
            ],
        )

        # Explicitly fetch tags after clone
        origin = repo.remotes.origin
        origin.fetch(tags=True)

        # Fetch the tags from the repository
        tags = [tag.name for tag in repo.tags]

        logging.debug(f"found tags: {str(tags)}")
        return tags

    except GitCommandError as e:
        logging.error(f"Git error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Clean up the temporary directory
        logging.debug(f"cleaning up temporary directory: {target_path}")
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

    # Return an empty list in case of any error
    return []


def pattern_is_regex(pattern: str) -> bool:
    """
    Determines if a string pattern is a regular expression.

    This function inspects the given string pattern to check if it contains
    any indicators that commonly denote a regular expression. It specifically
    looks for characters such as '*', '+', '[', ']', '{', and '}'.

    Args:
        pattern (str): The string pattern to evaluate for regular expression indicators.

    Returns:
        bool: True if the pattern contains regular expression indicators,
        False otherwise.
    """
    indicators = ["*", "+", "[", "]", "{", "}"]
    for indicator in indicators:
        if indicator in pattern:
            return True
    return False


def get_matching_refs(pattern: str, git_repo: GitRepo, creds: Creds) -> List[str]:
    """
    Gets all matching references in a remote Git repository based on a provided pattern.

    This function connects to a remote Git repository using provided credentials, retrieves
    all the references (e.g., tags) from the repository, and matches them against a supplied
    regular expression pattern. Matching references are stored and returned as a list. It also
    logs matching references and errors encountered during pattern matching.

    Args:
        pattern (str): The regular expression pattern to match references against.
        git_repo (GitRepo): The Git repository containing the source repository details.
        creds (Creds): The credentials required to access the Git repository.

    Returns:
        List[str]: A list of references that match the supplied pattern.

    Raises:
        Any exceptions occurring during execution are caught and logged without being raised.
    """
    matching_refs = []
    logging.debug(f"getting matching refs for pattern: {pattern}")
    src_creds = creds.get_git_creds(name=git_repo.source_repo_host)

    all_refs = get_all_tags_remote(
        repo_url=git_repo.source_repo,
        username=src_creds.username,
        password=src_creds.password,
        ssh_key_path=src_creds.ssh_key_path,
        target_path="./tmp/sync_tmp",
    )

    logging.info(f"found refs: {str(all_refs)}")
    for ref in all_refs:
        try:
            if re.match(pattern, ref):
                matching_refs.append(ref)
                logging.info(f"matched ref [{pattern}]: {ref}")
        except Exception as e:
            logging.error(f"Error matching pattern: {e}")
    logging.info(f"pattern matched refs: {str(matching_refs)}")
    return matching_refs
