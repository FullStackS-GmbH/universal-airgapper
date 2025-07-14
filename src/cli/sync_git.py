import logging
from typing import Literal

from models.creds.creds import Creds
from models.rc import RC
from models.resources.git import GitRepo
from repositories.pull import clone_repo_ref
from repositories.push import push_repo_ref
from repositories.utils import get_matching_refs, pattern_is_regex


def sync_repo(repo: GitRepo, creds: Creds) -> RC:
    """
    Synchronize the specified Git repository by processing its references.

    This function processes the repository and its associated references (refs),
    syncing those that match the given patterns while skipping duplicates. It uses
    credentials and push mode to perform the synchronization. The function handles
    regex patterns in references and collects the results of each synchronization
    operation. The combined results, indicating the overall success or failure,
    are returned as an RC object.

    Args:
        repo (GitRepo): A GitRepo object representing the repository to sync. It
            contains the references, source repository, and push mode information.
        creds (Creds): A Creds object containing credentials to authenticate
            against the Git repository.

    Returns:
        RC: An RC object that represents the result of the synchronization
            operation. It contains the success status, a list of processed entities,
            and other related details.
    """
    logging.info(f"processing repo: {repo.source_repo}")
    if not repo.refs:
        msg = "No refs specified for Git repository"
        logging.error(msg)
        return RC(ok=False, sync_cnt=True, msg=msg, ref=f"{repo.source_repo}")

    rc = RC(ok=False, ref=f"{repo.source_repo}", entity=[])

    all_refs = []

    for pattern in repo.refs:
        logging.info(f"processing repo ref pattern: {pattern}")

        if pattern_is_regex(pattern):
            logging.info(f"identified pattern as regex: {pattern}")
            refs = get_matching_refs(pattern=pattern, git_repo=repo, creds=creds)
        else:
            logging.info(f"identified pattern as fixed ref: {pattern}")
            refs = [pattern]

        for ref in refs:
            if ref in all_refs:
                logging.info(f"skipping ref - already processed: {repo.source_repo}:{ref}")
            else:
                logging.info(f"working on ref: {ref}")
                all_refs.append(ref)

                _rc = _sync_repo_ref(
                    git_repo=repo,
                    ref=ref,
                    credentials=creds,
                    push_mode=repo.push_mode,
                )
                _rc.sync_cnt = True
                _rc.type = "git"
                _rc.ref = f"{repo.source_repo}:{ref}"
                rc.entity.append(_rc)

    for _rc in rc.entity:
        if not _rc.ok:
            rc.ok = False
            break
    return rc


def _sync_repo_ref(
    git_repo: GitRepo,
    ref: str,
    credentials: Creds,
    push_mode: Literal["push", "skip", "force"] = "push",
) -> RC:
    """
    Synchronizes a specific reference from a source Git repository to a target Git repository.

    This function pulls a specific reference (branch, tag, or commit) from a source Git repository
    and pushes it to a target Git repository. Authentication credentials are retrieved dynamically
    for both the source and target repositories. If the operation fails at any step (clone or push),
    an appropriate response code is returned to indicate the nature of the failure. Temporary local
    storage is used during synchronization, which is cleaned automatically by the calling process.

    Args:
        git_repo (GitRepo): A representation of the source and target Git repositories,
            including their URLs and hosts.
        ref (str): The Git reference (e.g., branch name, commit hash, or tag) to be synchronized.
        credentials (Creds): Credentials manager to retrieve authentication details for
            both the source and target repositories.
        push_mode (Literal["push", "skip", "force"], optional): Determines the push behavior.
            Options include "push" (standard push), "skip" (perform no push), or "force"
            (forcefully update the target reference). Defaults to "push".

    Returns:
        RC: Response code object indicating the success or failure of the synchronization operation.
    """
    logging.info(f"pulling Git repo {git_repo.source_repo}:{ref}")
    folder_name = "./tmp/sync_tmp"

    src_creds = credentials.get_git_creds(name=git_repo.source_repo_host)
    _rc = clone_repo_ref(
        repo_url=git_repo.source_repo,
        target_path=folder_name,
        ref=ref,
        username=src_creds.username,
        password=src_creds.password,
        ssh_key_path=src_creds.ssh_key_path,
    )
    if not _rc.ok:
        return _rc

    logging.info(f"pushing to Git repo {git_repo.target_repo}:{ref}")
    tgt_creds = credentials.get_git_creds(name=git_repo.target_repo_host)
    _rc = push_repo_ref(
        local_repo_path=folder_name,
        remote_url=git_repo.target_repo,
        ref=ref,
        username=tgt_creds.username,
        password=tgt_creds.password,
        ssh_key_path=tgt_creds.ssh_key_path,
        push_mode=push_mode,
    )
    if _rc.ok:
        logging.info(f"sync done: {git_repo.source_repo}:{ref}")
    else:
        logging.error(f"sync failed: {git_repo.source_repo}:{ref}")
    return _rc
