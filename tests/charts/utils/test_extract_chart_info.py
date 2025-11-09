# test_utils.py
import os

from cnairgapper.charts.utils import extract_chart_info


def test_extract_chart_info_longhorn_1_7_2():
    """Test extract_chart_info using the pre-existing Helm chart
    located at <project-root>/tests/data/longhorn-1.7.2.tgz.
    """
    chart_path = os.path.abspath("tests/data/longhorn-1.7.2.tgz")

    result = extract_chart_info(chart_path)
    assert result == {"name": "longhorn", "version": "1.7.2"}
