import logging

from ..images.pull import pull_container_image
from ..images.push import push_container_image
from ..images.utils import check_image_tag_exists
from ..models.creds.creds import Creds
from ..models.rc import RC
from ..models.resources.image import Image
from ..models.scanner.scanners import Scanners


def sync_image(image: Image, credentials: Creds, scanners: Scanners) -> RC:
    """Synchronizes a container image with associated tags by validating scanning
    configurations and performing scan and sync operations. The function processes
    each tag of a Docker image sequentially, scans the image, and attempts to
    synchronize if scanning is successful. Returns a comprehensive result object
    indicating the outcome for each tag and the overall image.

    Args:
        image (Image): The container image to be synchronized, including its scan
            configuration and tags.
        credentials (Creds): The credentials object providing login details for
            image registry access.
        scanners (Scanners): A Scanners object containing scanner configurations
            and providing scanning functionality.

    Returns:
        RC: An object representing the synchronization result. The `ok` field
            denotes the overall success. The `entity` field contains the outcome
            for each image tag.

    Raises:
        None
    """
    # get scan config by name
    scanner = scanners.get_scanner(image.scan)
    tgt_creds = credentials.get_image_creds(name=image.target_registry)

    if image.scan and not scanner:
        msg = f"No scan config provided for scanning image: {image.source}"
        logging.error(msg)
        return RC(ok=False, msg=msg, ref=f"{image.source}")

    logging.info(f"processing image: {image.source}")
    if not image.tags:
        msg = f"No tags specified for Docker image {image.source}"
        logging.error(msg)
        return RC(ok=False, msg=msg, ref=f"{image.source}")

    rc = RC(ok=True, ref=f"{image.source}", entity=[])
    for tag in image.tags:
        logging.info(f"processing image tag: {image.source}:{tag}")
        _rc = check_image_tag_exists(
            image=image,
            tag=tag,
            username=tgt_creds.username,
            password=tgt_creds.password,
        )
        image_exists = _rc.ok
        logging.debug(f"image exists [{_rc.ok!s}]: {_rc.msg}")
        _rc.sync_cnt = True
        _rc.type = "docker"
        _rc.ref = f"{image.source}:{tag}"

        if _rc.err:
            # failure while checking for existence
            rc.entity.append(_rc)
            continue

        if (image_exists and image.push_mode == "force") or not image_exists:
            # image does not exist yet, or force sync is activated
            image_okay = True
            if image.scan:
                logging.info(f"scanning image with {scanner.name}")
                scan_rc = scanner.scan_image(
                    image=image,
                    tag=tag,
                    registry_username=credentials.get_image_creds(
                        name=image.source_registry
                    ).username,
                    registry_password=credentials.get_image_creds(
                        name=image.source_registry
                    ).password,
                )
                logging.debug(f"scanning ok [{scan_rc.ok!s}]: {scan_rc.msg}")
                image_okay = scan_rc.ok
                if not scan_rc.ok:
                    _rc.ok = False
                    _rc.msg = scan_rc.msg
            if image_okay:
                logging.info(f"starting sync for {image.source}:{tag} ...")
                sync_rc = _sync_image_tag(
                    image=image,
                    tag=tag,
                    credentials=credentials,
                )
                if not sync_rc.ok:
                    _rc.msg = sync_rc.msg
                else:
                    _rc.msg = f"synced tag: {image.source}:{tag}"
                logging.debug(f"sync finished [{sync_rc.ok!s}]: {sync_rc.msg}")
                _rc.ok = sync_rc.ok
        else:
            _rc.msg = f"skipping tag - already exists: {image.source}:{tag}"
            logging.info(_rc.msg)

        rc.entity.append(_rc)
    # did we have any error?
    for _rc in rc.entity:
        if not _rc.ok:
            rc.ok = False
            break
    return rc


def _sync_image_tag(image: Image, tag: str, credentials: Creds) -> RC:
    """Synchronizes a specific image tag between a source and target container registry.

    This function checks if the specified image tag exists in the target registry.
    If it doesn't exist, it pulls the image from the source registry to a local
    temporary folder, and then pushes it to the target registry. If the image tag
    already exists in the target registry, it skips the synchronization process
    and logs this information.

    Args:
        image (Image): Contains information about the source and target
            image names, repositories, and registries involved in the sync
            process.
        tag (str): The specific tag of the container image to be synchronized.
        credentials (Creds): Handles authentication for accessing both the source
            and target container registries.

    Returns:
        RC: An object representing the result of the synchronization
            operation, containing information about success or failure,
            an accompanying message, and a reference to the target image.
    """
    src_creds = credentials.get_image_creds(name=image.source_registry)
    tgt_creds = credentials.get_image_creds(name=image.target_registry)
    folder_name = "./tmp/sync_tmp"

    logging.info(f"Pulling Docker image {image.source}:{tag}")
    rc = pull_container_image(
        image_name=image.source_repo,
        tag=tag,
        registry=image.source_registry,
        username=src_creds.username,
        password=src_creds.password,
        output_dir=folder_name,
    )
    if not rc.ok:
        logging.error(rc.msg)
        return rc
    logging.info(f"Pushing Docker image {image.target}:{tag}")
    rc = push_container_image(
        src_image_dir=folder_name,
        tgt_registry=image.target_registry,
        tgt_image_name=image.target_repo,
        tgt_image_tag=tag,
        username=tgt_creds.username,
        password=tgt_creds.password,
    )
    if rc.ok:
        logging.info(f"sync done: {image.target}:{tag}")
    return rc
