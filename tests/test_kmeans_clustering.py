import unittest.mock as mock
from pathlib import Path
import os

import numpy as np
import pytest

from geojson import FeatureCollection, Feature
import rasterio as rio

from blockutils.common import ensure_data_directories_exist, TestDirectoryContext
from blockutils.syntheticimage import SyntheticImage
from blockutils.exceptions import UP42Error

from context import KMeansClustering, raise_if_too_large


@pytest.fixture(scope="session", autouse=True)
def fixture():
    ensure_data_directories_exist()


def test_kmeans_clustering():
    lcc = KMeansClustering(n_clusters=5, n_iterations=5, n_sieve_pixels=1)
    input_ar = np.random.uniform(0, 255, 30000).reshape(100, 100, 3)
    clusters_ar = lcc.run_kmeans(input_ar)
    assert len(clusters_ar.flatten()) == 10000
    assert len(np.unique(clusters_ar)) == 5
    assert np.min(clusters_ar) == 0
    assert np.max(clusters_ar) == 4

    lcc = KMeansClustering(n_clusters=3, n_iterations=8, n_sieve_pixels=16)
    input_ar = np.random.uniform(0, 10, 400000).reshape(200, 200, 10)
    clusters_ar = lcc.run_kmeans(input_ar)
    assert len(clusters_ar.flatten()) == 40000
    assert len(np.unique(clusters_ar)) == 3
    assert np.min(clusters_ar) == 0
    assert np.max(clusters_ar) == 2


def test_process():
    lcc = KMeansClustering(n_clusters=5, n_iterations=5, n_sieve_pixels=1)
    with TestDirectoryContext(Path("/tmp")) as temp:
        image_path, _ = SyntheticImage(
            100, 100, 4, "uint16", out_dir=temp / "input", nodata=-1
        ).create(seed=100)
        input_fc = FeatureCollection(
            [
                Feature(
                    geometry={
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-8.89411926269531, 38.61687046392973],
                                [-8.8604736328125, 38.61687046392973],
                                [-8.8604736328125, 38.63939998171362],
                                [-8.89411926269531, 38.63939998171362],
                                [-8.89411926269531, 38.61687046392973],
                            ]
                        ],
                    },
                    properties={"up42.data_path": str(image_path.name)},
                )
            ]
        )
        output_fc = lcc.process(input_fc)
        assert output_fc.features


def test_process_float_with_nodata():
    lcc = KMeansClustering(n_clusters=5, n_iterations=5, n_sieve_pixels=1)
    with TestDirectoryContext(Path("/tmp")) as temp:
        image_path, _ = SyntheticImage(
            100, 100, 4, "float", out_dir=temp / "input", nodata=-9999.0, nodata_fill=5
        ).create(seed=100)
        input_fc = FeatureCollection(
            [
                Feature(
                    geometry={
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-8.89411926269531, 38.61687046392973],
                                [-8.8604736328125, 38.61687046392973],
                                [-8.8604736328125, 38.63939998171362],
                                [-8.89411926269531, 38.63939998171362],
                                [-8.89411926269531, 38.61687046392973],
                            ]
                        ],
                    },
                    properties={"up42.data_path": str(image_path.name)},
                )
            ]
        )
        output_fc = lcc.process(input_fc)
        assert output_fc.features

        with rio.open(
            os.path.join(
                "/tmp/output", output_fc.features[0]["properties"]["up42.data_path"]
            )
        ) as src:
            assert src.meta["nodata"] == 255
            band = src.read(1)
            assert np.all(band[:5, :5] == 255)


def test_raise_if_too_large():
    with mock.patch("rasterio.DatasetReader") as src:
        instance = src.return_value
        instance.meta["dtype"] = "uint8"
        instance.count = 4
        instance.shape = (10, 10)
        raise_if_too_large(instance)

        with pytest.raises(UP42Error, match=r".*[WRONG_INPUT_ERROR].*"):
            instance.meta = {"dtype": "float32"}
            instance.count = 4
            instance.shape = (500000, 500000)
            raise_if_too_large(instance)

        with pytest.raises(UP42Error, match=r".*[WRONG_INPUT_ERROR].*"):
            instance.meta = {"dtype": "uint8"}
            instance.count = 4
            instance.shape = (500000, 500000)
            raise_if_too_large(instance)

        with pytest.raises(UP42Error, match=r".*[WRONG_INPUT_ERROR].*"):
            instance.meta = {"dtype": "uint16"}
            instance.count = 4
            instance.shape = (500000, 500000)
            raise_if_too_large(instance)

        with pytest.raises(UP42Error, match=r".*[WRONG_INPUT_ERROR].*"):
            instance.meta = {"dtype": "uint8"}
            instance.count = 4
            instance.shape = (10, 10)
            raise_if_too_large(instance, 1)

        with pytest.raises(UP42Error, match=r".*[WRONG_INPUT_ERROR].*"):
            instance.meta = {"dtype": "float32"}
            instance.count = 1
            instance.shape = (28873, 22291)
            raise_if_too_large(instance)
