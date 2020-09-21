"""
End-to-end test: Fetches data, creates output, stores it in /tmp and checks if output
is valid.
"""
from pathlib import Path
import os

import geojson

from blockutils.logging import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    TESTNAME = "e2e_k-means_clustering"
    TEST_DIR = Path("/tmp") / TESTNAME
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR = TEST_DIR / "input"
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    FILES_TO_DELETE = Path(TEST_DIR / "output").glob("*")
    for file_path in FILES_TO_DELETE:
        file_path.unlink()

    # Download file from gsutil
    os.system(
        "gsutil -m cp -r gs://floss-blocks-e2e-testing/e2e_kmeans_clustering/* %s"
        % INPUT_DIR
    )

    RUN_CMD = (
        """docker run -v %s:/tmp \
                 -e 'UP42_TASK_PARAMETERS={"n_clusters":8, "n_iterations": 10, "n_sieve_pixels": 64}' \
                  -it kmeans-clustering"""
        % TEST_DIR
    )

    os.system(RUN_CMD)

    # Print out bbox of one tile
    GEOJSON_PATH = TEST_DIR / "output" / "data.json"

    with open(str(GEOJSON_PATH)) as f:
        FEATURE_COLLECTION = geojson.load(f)

    logger.info(FEATURE_COLLECTION.features[0].bbox)

    OUTPUT = (
        TEST_DIR
        / "output"
        / Path(FEATURE_COLLECTION.features[0].properties["up42.data_path"])
    )

    logger.info(OUTPUT)

    assert OUTPUT.exists()
