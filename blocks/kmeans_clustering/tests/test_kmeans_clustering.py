import numpy as np
import pytest

from context import KMeansClustering

from context import ensure_data_directories_exist


@pytest.fixture(scope="session", autouse=True)
def fixture():
    ensure_data_directories_exist()


def test_kmeans_clustering():
    lcc = KMeansClustering(n_clusters=5, n_iter=5, n_sieve_pixels=1)
    input_ar = np.random.uniform(0, 255, 30000).reshape(100, 100, 3)
    clusters_ar = lcc.run_kmeans(input_ar)
    assert len(clusters_ar.flatten()) == 10000
    assert len(np.unique(clusters_ar)) == 5
    assert np.min(clusters_ar) == 0
    assert np.max(clusters_ar) == 4

    lcc = KMeansClustering(n_clusters=3, n_iter=8, n_sieve_pixels=16)
    input_ar = np.random.uniform(0, 10, 400000).reshape(200, 200, 10)
    clusters_ar = lcc.run_kmeans(input_ar)
    assert len(clusters_ar.flatten()) == 40000
    assert len(np.unique(clusters_ar)) == 3
    assert np.min(clusters_ar) == 0
    assert np.max(clusters_ar) == 2
