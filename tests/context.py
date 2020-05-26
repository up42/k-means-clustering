import os
import sys

# pylint: disable=unused-import
from src.kmeans_clustering import KMeansClustering

# Path hacks to make the code available for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
