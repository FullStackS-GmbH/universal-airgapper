from models.config.config_helm_chart import ConfigHelmChart


class HelmChart:
    """
    Represents a Helm Chart and its associated metadata.

    This class encapsulates information about a Helm Chart, providing properties for
    managing chart sources, target repositories, versions, and push modes. It can be
    used to retrieve chart-specific details such as the chart name.

    Attributes:
        source: Source path or URL of the Helm Chart.
        source_registry: Registry for the source Helm Chart.
        target_repo: Repository where the Helm Chart will be stored.
        target_registry: Target registry for the Helm Chart.
        version: Version of the Helm Chart.
        push_mode: Mode used to push the Helm Chart (e.g., overwrite, append).
    """

    def __init__(self, config_chart: ConfigHelmChart, version: str):
        self.source = config_chart.source_chart
        self.source_registry = config_chart.source_registry
        self.target_repo = config_chart.target_repo
        self.target_repo_type = config_chart.target_repo_type
        self.target_registry = config_chart.target_registry
        self.version = version
        self.push_mode = config_chart.push_mode

    @property
    def chart_name(self):
        """get chart name"""
        if "/" in self.source:
            return self.source.split("/")[-1]
        return self.source
