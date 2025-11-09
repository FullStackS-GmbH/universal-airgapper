import logging
import os
from pathlib import Path
from typing import Literal

from git import Repo

from ..models.rc import RC

PushMode = Literal["skip", "push", "force"]


def push_repo_ref(
    local_repo_path: str | Path,
    remote_url: str,
    ref: str,
    push_mode: PushMode = "push",
    username: str | None = None,
    password: str | None = None,
    ssh_key_path: str | None = None,
) -> RC:
    """Handles pushing a specific Git reference from a local repository to a remote
    repository using different modes and optional authentication methods.

    Args:
        local_repo_path (str | Path): The local repository path from which the reference
            should be pushed. This can be a string path or a Path object.
        remote_url (str): URL of the remote repository to which the reference will be
            pushed.
        ref (str): The name of the reference (branch or tag) to be pushed.
        push_mode (PushMode, optional): Determines how the reference is pushed.
            defaults to "push".
            If set to "push", the reference is pushed normally.
            If "force", it overrides any existing remote reference.
            If "skip", the push will be skipped if the reference already exists.
        username (Optional[str], optional): Username for HTTPS-based authentication.
            Required only if the `remote_url` uses HTTPS without a pre-configured
            authentication method.
        password (Optional[str], optional): Password for HTTPS-based authentication,
            required along with `username`. An optional environment variable name can
            also be provided for advanced authentication configurations.
        ssh_key_path (Optional[str], optional):
            Path to the SSH private key used for SSH-based authentication.
            Required only if the `remote_url` uses SSH and an explicit key is needed.

    Returns:
        RC: A result object summarizing the outcome of the push. Contains `ok` (bool)
            indicating success or failure, a `message` (str) detailing the result,
            and `ref` (str) specifying the pushed reference.

    Raises:
        Exception: If an error occurs during the push process, it is caught and logged,
        and the function returns a failure `RC` instance instead of propagating the
        error.
    """
    try:
        # Convert path to Path object
        repo_path = Path(local_repo_path)

        # Open the repository
        repo = Repo(repo_path)

        # Configure authentication
        if remote_url.startswith("https://"):
            if username and password:
                # Format HTTPS URL with credentials
                parsed_url = remote_url.replace("https://", "")
                remote_url = f"https://{username}:{password}@{parsed_url}"
        elif remote_url.startswith("git@") and ssh_key_path:
            # Configure SSH key if provided
            os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path}"

        # Add remote if it doesn't exist
        remote_name = "push_remote"
        try:
            remote = repo.remote(remote_name)
            remote.set_url(remote_url)
        except ValueError:
            remote = repo.create_remote(remote_name, remote_url)

        # Fetch remote refs
        remote.fetch()

        # Check if ref exists in remote
        remote_refs = [str(r.remote_head) for r in remote.refs]
        ref_exists = ref in remote_refs

        if ref_exists:
            if push_mode == "skip":
                msg = f"Ref {ref} already exists in remote, skipping push"
                logging.info(msg)
                return RC(ok=True, msg=msg, ref=ref)
            if push_mode == "force":
                logging.info(f"Force pushing ref {ref}")
                push_info = remote.push(f"+{ref}")  # '+' prefix forces the push
            else:  # push_mode == 'push'
                logging.info(f"Pushing ref {ref}")
                push_info = remote.push(ref)
        else:
            logging.info(f"Pushing new ref {ref}")
            push_info = remote.push(ref)

        # Check if push was successful
        if push_info[0].flags & push_info[0].ERROR:
            msg = f"Failed to push ref {ref}"
            logging.error(msg)
            return RC(ok=False, msg=msg, ref=ref)

        return RC(ok=True, ref=ref)

    except Exception as e:
        msg = f"Error pushing to remote: {e!s}"
        logging.exception(msg)
        return RC(ok=False, msg=msg, ref=ref)
