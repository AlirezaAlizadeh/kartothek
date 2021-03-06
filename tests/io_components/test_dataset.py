"""

This module tests high level dataset API functions which require entire datasets, indices, etc

"""
from collections import OrderedDict

import pandas as pd
import pandas.testing as pdt
import pytest

from kartothek.core.dataset import DatasetMetadata
from kartothek.core.index import ExplicitSecondaryIndex


@pytest.mark.min_metadata_version(4)
def test_dataset_get_indices_as_dataframe_raise_index_not_loaded(dataset_with_index):
    with pytest.raises(RuntimeError):
        dataset_with_index.get_indices_as_dataframe(
            columns=dataset_with_index.partition_keys
        )


@pytest.mark.min_metadata_version(4)
def test_dataset_get_indices_as_dataframe_partition_keys_only(
    dataset_with_index, store_session
):
    expected = pd.DataFrame(
        OrderedDict([("P", [1, 2])]),
        index=pd.Index(["P=1/cluster_1", "P=2/cluster_2"], name="partition"),
    )
    ds = dataset_with_index.load_partition_indices()
    result = ds.get_indices_as_dataframe(columns=dataset_with_index.partition_keys)
    pdt.assert_frame_equal(result, expected)


@pytest.mark.min_metadata_version(4)
def test_dataset_get_indices_as_dataframe(dataset_with_index, store_session):
    expected = pd.DataFrame(
        OrderedDict([("L", [1, 2]), ("P", [1, 2])]),
        index=pd.Index(["P=1/cluster_1", "P=2/cluster_2"], name="partition"),
    )
    ds = dataset_with_index.load_partition_indices()
    ds = ds.load_index("L", store_session)

    result = ds.get_indices_as_dataframe()
    pdt.assert_frame_equal(result, expected)


def test_dataset_get_indices_as_dataframe_duplicates():
    ds = DatasetMetadata(
        "some_uuid",
        indices={
            "l_external_code": ExplicitSecondaryIndex(
                "l_external_code", {"1": ["part1", "part2"], "2": ["part1", "part2"]}
            ),
            "p_external_code": ExplicitSecondaryIndex(
                "p_external_code", {"1": ["part1"], "2": ["part2"]}
            ),
        },
    )
    expected = pd.DataFrame(
        OrderedDict(
            [
                ("p_external_code", ["1", "1", "2", "2"]),
                ("l_external_code", ["1", "2", "1", "2"]),
            ]
        ),
        index=pd.Index(["part1", "part1", "part2", "part2"], name="partition"),
    )
    result = ds.get_indices_as_dataframe()
    pdt.assert_frame_equal(result, expected)
