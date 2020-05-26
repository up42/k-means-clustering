from typing import List
from pathlib import Path

# Feature is used for typing, but mypy does not recongnize usage
# pylint: disable=unused-import
from geojson import FeatureCollection, Feature
import numpy as np
import rasterio as rio
from rasterio import features
from sklearn.cluster import KMeans

from blockutils.logging import get_logger
from blockutils.blocks import ProcessingBlock

logger = get_logger(__name__)


class KMeansClustering(ProcessingBlock):
    """
    This class implements a K-means clustering method
    """

    def __init__(self, n_clusters: int = 6, n_iter: int = 10, n_sieve_pixels: int = 64):
        """
        It is possible to set all parameters for testing etc, but in a standard scenario
        these values would be read from env variables

        :param n_clusters: Number of clusters for the K-means classification
        :param n_iter: Number of iterations for the K-means classification
        :param n_sieve_pixels: Minimum size (in pixels) of the cluster patches for the sieve-ing operation
        """
        super().__init__()
        self.n_clusters = n_clusters
        self.n_iterations = n_iter
        self.n_sieve_pixels = n_sieve_pixels

    def run_kmeans(self, img_ar: np.ndarray) -> np.ndarray:
        """
        This method implements the actual K-means clustering algorithm. It takes the input points in an numpy ndarray
        and returns the list of cluster center indices in another one

        :param img_ar: The input data has to be a 3D numpy ndarray: (image_width, image_height, image_bands)
        :return: The cluster center indices of the input points in a 2D ndarray: (image_width, image_height, 1)
        """
        # Get image dimensions
        img_width = img_ar.shape[0]
        img_height = img_ar.shape[1]
        img_bands = img_ar.shape[2]

        # Prepare input data
        flatten_arr = img_ar.reshape(img_width * img_height, img_bands)

        # Run scikit-learn K-means
        k_means = KMeans(n_clusters=self.n_clusters, n_init=self.n_iterations)
        _ = k_means.fit(flatten_arr)
        cluster_indices = k_means.labels_
        cluster_indices = cluster_indices.reshape((img_width, img_height))

        # Run sieve operation to reduce noise by eliminating small pixel patches
        if self.n_sieve_pixels > 0:
            cluster_indices = features.sieve(
                cluster_indices.astype(rio.int16), self.n_sieve_pixels
            ).astype(np.int16)

        return cluster_indices

    def run_kmeans_clustering(self, input_file_path: str, output_file_path: str):
        """
        This method reads the input file, runs the K-means clustering on the raster data points and writes the results
        to the output file

        :param input_file_path: The location of the input file on the file system
        :param output_file_path: The location of the output file on the file system
        """

        # Read data from the geo tif file
        with rio.open(input_file_path, "r") as src:
            img_band_cnt = src.meta["count"]
            img_bands = []
            for i in range(img_band_cnt):
                img_bands.append(src.read(i + 1))
        img_ar = np.moveaxis(np.stack(img_bands), 0, 2)
        logger.info("src.meta:")
        logger.info(src.meta)

        # Call clustering operation
        clusters_ar = self.run_kmeans(img_ar)

        # Copy geo tif metadata to the output image and write it to a file
        dst_meta = src.meta.copy()
        dst_meta["count"] = 1
        dst_meta["dtype"] = "uint8"
        logger.info("dst_meta:")
        logger.info(dst_meta)
        with rio.open(output_file_path, "w", **dst_meta) as dst:
            dst.write(clusters_ar.astype(rio.uint8), 1)

    def process(self, input_fc: FeatureCollection) -> FeatureCollection:
        """
        Given the necessary parameters and a feature collection describing the input datasets,
        run K-means clustering for each input data set and create output feature collection

        :param metadata: A GeoJSON FeatureCollection describing all input datasets
        :return: A GeoJSON FeatureCollection describing all output datasets
        """
        results = []  # type: List[Feature]
        for feature in input_fc.features:
            path_to_input_img = feature["properties"]["up42.data_path"]
            path_to_output_img = Path(path_to_input_img).stem + "_kmeans.tif"

            out_feature = feature.copy()
            out_feature["properties"]["up42.data_path"] = path_to_output_img
            results.append(out_feature)

            self.run_kmeans_clustering(
                "/tmp/input/" + path_to_input_img, "/tmp/output/" + path_to_output_img
            )
        return FeatureCollection(results)
