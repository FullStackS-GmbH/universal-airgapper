import logging

from charts.pull import pull_helm_chart
from charts.push import push_helm_chart
from charts.utils import get_auth_headers, oci_chart_exists
from models.config.config_helm_chart import ConfigHelmChart
from models.creds.creds import Creds
from models.rc import RC
from models.resources.helm import HelmChart


def sync_chart(chart_config: ConfigHelmChart, credentials: Creds) -> RC:
    """
    Synchronizes a Helm chart with specified configurations and credentials, processing
    chart versions and determining their synchronization results.

    Args:
        chart_config (ConfigHelmChart): The configuration object for the Helm chart,
            including source details and version specifications.
        credentials (Creds): The credentials required for accessing and synchronizing
            the Helm chart.

    Returns:
        RC: A result container object that encapsulates the synchronization results,
            status, references, and entity details of the processed chart versions.

    Raises:
        KeyError: Raised implicitly if required attributes are missing in the input
            objects during processing.
        ValueError: Raised implicitly during incorrect or incompatible input during
            version processing within the defined functions.
    """
    logging.info(f"processing chart: {chart_config.source_chart}")
    if not chart_config.versions:
        msg = f"No versions specified for Helm chart {chart_config.source_chart}"
        logging.error(msg)
        return RC(
            ok=False,
            sync_cnt=True,
            type="helm",
            msg=msg,
            ref=f"{chart_config.source_registry} - {chart_config.source_chart}",
        )

    rc = RC(
        ok=True,
        type="helm",
        ref=f"{chart_config.source_registry} - {chart_config.source_chart}",
        entity=[],
    )
    for version in chart_config.versions:
        chart = HelmChart(chart_config, version)
        logging.info(f"processing chart version: {chart.chart_name}:{version}")
        _rc = _sync_chart_version(
            chart=chart,
            creds=credentials,
        )
        _rc.sync_cnt = True
        _rc.type = "helm"
        _rc.ref = f"{chart_config.source_registry} - {chart_config.source_chart}:{version}"
        rc.entity.append(_rc)
    for _rc in rc.entity:
        if not _rc.ok:
            rc.ok = False
            break
    return rc


def _sync_chart_version(
    chart: HelmChart,
    creds: Creds,
) -> RC:
    """
    Synchronizes a Helm chart version between source and target registries.

    This function handles the process of ensuring that the specified Helm chart
    exists in the target registry by pulling the Helm chart from the source
    registry, if necessary, and pushing it to the target registry. It checks
    if the chart already exists in the target registry and skips the upload
    process if the chart is configured to be skipped. Temporary files during
    the process are stored in a predefined local directory.

    Args:
        chart (HelmChart): The details of the Helm chart to be synchronized,
            including source and target registry details, chart name,
            version, and push mode.
        creds (Creds): Authentication credentials used to generate the
            headers required for accessing the source and target registries.

    Returns:
        RC: An instance of RC that represents the result of the synchronization
            operation, including its status (success or failure), error details
            if any, and reference details when applicable.
    """
    logging.info(f"pulling [{chart.source_registry}] {chart.chart_name} : {chart.version}")
    folder_name = "./tmp/sync_tmp"

    # src_headers = get_auth_headers(creds=creds, registry=chart.source_registry, repo=chart.source)
    src_headers = get_auth_headers(creds=creds, registry=chart.source_registry)
    # tgt_headers = get_auth_headers( creds=creds, registry=chart.target_registry,
    # repo=chart.target_repo )
    tgt_headers = get_auth_headers(creds=creds, registry=chart.target_registry)

    _rc = oci_chart_exists(chart=chart, headers=tgt_headers)
    # chart exists and can be skipped
    if _rc.err:
        return _rc

    if _rc.ok and chart.push_mode == "skip":
        msg = f"skip chart upload: {chart.chart_name} : {chart.version}"
        logging.info(msg)
        return RC(ok=True, msg=msg)

    _rc = pull_helm_chart(
        chart_path=chart.source,
        version=chart.version,
        registry_url=chart.source_registry,
        output_dir=folder_name,
        headers=src_headers,
    )
    if not _rc.ok:
        return _rc

    logging.info(f"pushing [{chart.target_registry}] repo - {chart.target_repo} : {chart.version}")
    _rc = push_helm_chart(
        chart_path=_rc.ref,
        repo_type=chart.target_repo_type,
        repo_url=chart.target_registry,
        repo_path=chart.target_repo,
        headers=tgt_headers,
    )
    logging.info(f"sync done - {chart.chart_name} : {chart.version}")
    return _rc
