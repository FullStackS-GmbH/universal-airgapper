from typing import Literal

from pydantic import BaseModel, Field


class ConfigHelmChart(BaseModel):
    """
    Represents the configuration parameters required for a Helm chart.

    This class is used to define and validate the configuration details needed for
    managing Helm chart synchronization. It includes information about source and
    target registries, source chart location, chart versions to sync, and push modes.

    Attributes:
        type (str): Object of type 'helm'.
        source_registry (str): Source registry of the Helm chart. Can be an OCI
            or legacy registry. For example, https://charts.jetstack.io or
            oci://registry-1.docker.io/.
        source_chart (str): Source chart name or location of the Helm chart. For
            example, bitnami/mongodb or cert-manager.
        target_registry (str): Target registry of the Helm chart, which can be
            OCI or legacy registry.
        target_repo (str): Target repository of the Helm chart.
        versions (list[str]): List of Helm chart versions to synchronize.
        push_mode (Literal["skip", "overwrite"]): Specifies the synchronization
            mode. Can either skip or overwrite if the target version already exists.
    """

    type: str = Field("helm", min_length=1, description="Object of type 'helm'")
    source_registry: str = Field(
        ...,
        min_length=1,
        description="""
            Source registry of the Helm chart, OCI or legacy.
            eg. https://charts.jetstack.io, oci://registry-1.docker.io/
        """,
    )
    source_chart: str = Field(
        ...,
        min_length=1,
        description="""
            Source chart name/location of the Helm chart.
            eg. bitnami/mongodb, cert-manager
      """,
    )
    target_registry: str = Field(
        ...,
        min_length=1,
        description="Target registry of the Helm chart, OCI or legacy.",
    )
    target_repo: str = Field(
        ..., min_length=1, description="Target repository of the Helm chart."
    )
    target_repo_type: Literal["oci", "nexus"] = Field(
        "oci", min_length=1, description="Target repository type."
    )
    versions: list[str] = Field(
        default_factory=list, description="List of Helm chart versions to sync."
    )
    push_mode: Literal["skip", "overwrite"] = Field(
        "skip", description="skip or overwrite if target version already exists"
    )
