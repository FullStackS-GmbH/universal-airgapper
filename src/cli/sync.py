from cli.sync_git import sync_repo
from cli.sync_helm import sync_chart
from cli.sync_image import sync_image
from models.config.config_file import ConfigFile
from models.config.config_resources import SyncResources
from models.creds.creds import Creds
from models.creds.creds_file import CredsFile
from models.rc import RC
from models.scanner.scanners import Scanners


def sync(creds_file: CredsFile, config_file: ConfigFile) -> RC:
    """
    Synchronizes resources specified in a configuration file using credentials.

    This function takes a credentials file and a configuration file as input.
    The configuration file specifies the resources to synchronize, which may include
    images, charts, and repositories. It uses the credentials to authorize synchronization
    actions and scanners to analyze the resources as required. The function aggregates
    the results of all synchronization actions into a single result object.

    Args:
        creds_file (CredsFile): A file containing the necessary credentials
            required for the synchronization of resources.
        config_file (ConfigFile): A configuration file specifying the resources
            and scanners to be used during the synchronization.

    Returns:
        RC: An object containing the overall status of the synchronization process
            and details about each entity processed. The `ok` attribute indicates
            the overall success or failure, while `entity` contains individual
            resource results.

    Raises:
        ValueError: If no resources are specified in the configuration file.

    """
    rc = RC(ok=True, entity=[])
    resources = config_file.resources
    if not resources:
        raise ValueError("no resources specified")

    # create SyncResources object
    sync_resources = SyncResources(resources)

    # prepare Credentials object
    creds = Creds(creds_file)

    # prepare list of scan configs
    scanners = Scanners([])
    for scanner in config_file.scanners:
        scanners.add_scanner(
            scanner, creds.get_scanner_creds(name=scanner.name, scanner_type=scanner.type)
        )

    for image in sync_resources.images:
        _rc = sync_image(image, creds, scanners)
        rc.entity.extend(_rc.entity)

    for chart in sync_resources.charts:
        _rc = sync_chart(chart, creds)
        rc.entity.extend(_rc.entity)

    for repo in sync_resources.repos:
        _rc = sync_repo(repo, creds)
        rc.entity.extend(_rc.entity)

    for _rc in rc.entity:
        if not _rc.ok:
            rc.ok = False
            break
    return rc
