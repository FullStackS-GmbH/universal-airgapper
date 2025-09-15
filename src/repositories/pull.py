import logging
import os
import shutil
from pathlib import Path

import git
from git import GitCommandError

from models.rc import RC


def clone_repo_ref(
    repo_url: str,
    ref: str,
    target_path: str,
    username: str | None = None,
    password: str | None = None,
    ssh_key_path: str | None = None,
) -> RC:
    """Clones a specific reference (branch, tag, or commit) from a Git repository and stores
    it in the specified target path.

    This function supports both SSH and HTTPS authentication for cloning repositories.
    It creates or cleans the target directory as needed. For HTTPS authentication,
        both username and password must be provided.
    For SSH authentication, an SSH key file path must be specified.
    The function logs errors encountered during the process and returns a result
        indicating success or failure.

    Args:
        repo_url (str): The URL of the repository to clone. Must start with "http" or "git@".
        ref (str): The specific branch, tag, or commit reference to clone.
        target_path (str): The file path where the repository will be cloned.
        username (Optional[str]): The username for HTTPS authentication.
        password (Optional[str]): The password for HTTPS authentication.
        ssh_key_path (Optional[str]): The file path to the SSH private key for SSH authentication.

    Returns:
        RC: An object indicating the result of the operation,
            including success/failure status and optional data.

    Raises:
        GitCommandError: Raised when git operations fail internally.
    """
    try:
        # Create target directory if it doesn't exist
        target_dir = Path(target_path)
        # Cleanup target path if requested
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        git_options = []
        # Configure authentication
        if repo_url.startswith("git@"):
            if not ssh_key_path:
                msg = "SSH key path is required for SSH authentication"
                logging.error(msg)
                return RC(ok=False, msg=msg)
            if not os.path.exists(ssh_key_path):
                msg = f"SSH key path {ssh_key_path} does not exist"
                logging.error(msg)
                return RC(ok=False, msg=msg)
            os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path}"
        elif username and password:
            if username == "AzureReposAuthnSucks":
                git_options.append(f"--config-env=http.extraheader={password}")
            else:
                logging.debug(f"using username [{username}] and password for HTTPS auth")
                # Use Git credential environment variable for authentication
                url_parts = repo_url.split("://")
                repo_url = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"
        elif username or password:
            msg = "Both username and password are required for HTTPS authentication"
            logging.error(msg)
            return RC(ok=False, msg=msg)

        # Clone the repository
        repo = git.Repo.clone_from(
            repo_url,
            target_path,
            branch=ref,
            single_branch=True,
            multi_options=git_options,
        )

        return RC(ok=True, entity=repo)

    except GitCommandError as e:
        msg = f"Failed to clone repository: {e.stderr!s}"
        logging.exception(msg)
        return RC(ok=False, msg=msg)
