import json
import logging
import os
import pathlib
from typing import Any, Union

from geojson import Feature, FeatureCollection

AOICLIPPED = "up42.data.aoiclipped"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def get_logger(name, level=logging.DEBUG):
    """
    This method creates logger object and sets the default log level to DEBUG
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def set_capability(feature: Feature, capability: str, value: Any) -> Feature:
    """
    This method is a simple setter for the capability field of the feature
    """
    feature["properties"][capability] = value
    return feature


def get_capability(feature: Feature, capability: str) -> Any:
    """
    This method is a simple getter for the capability field of the feature
    """
    return feature["properties"].get(capability)


def ensure_data_directories_exist():
    """
    This method checks input and output directories for data flow
    """
    pathlib.Path('/tmp/input/').mkdir(parents=True, exist_ok=True)
    pathlib.Path('/tmp/output/').mkdir(parents=True, exist_ok=True)


def save_metadata(result: FeatureCollection):
    """
    This method saves the feature collection meta data to the provided location
    """
    ensure_data_directories_exist()
    with open("/tmp/output/data.json", "w") as fp:
        fp.write(json.dumps(result))


def load_metadata() -> FeatureCollection:
    """
    Get the data from the provided location
    """
    ensure_data_directories_exist()
    if os.path.exists("/tmp/input/data.json"):
        with open("/tmp/input/data.json") as fp:
            data = json.loads(fp.read())

        features = []
        for feature in data["features"]:
            features.append(Feature(**feature))

        return FeatureCollection(features)
    else:
        return FeatureCollection([])


def safe_get_dict(data: Union[None, dict], key, default: dict) -> dict:
    """
    This method is a safe getter function that returns a dict entry in case that the dict is provided and it contains
    the key (where the value itself is a dict). Otherwise it returns the provided default value which is a dict itself.
    """
    if data is None:
        return default

    value = data.get(key, default)

    if value is None or not isinstance(value, dict):
        return default

    return value


def load_params() -> dict:
    """
    Get the parameters for the current task directly from the task parameters. If
    the task parameters are not set, falls back to the old INTERSTELLAR_JOB_INPUTS.
    """
    helper_logger = get_logger(__name__)
    data = os.environ.get("UP42_TASK_PARAMETERS", '{}')
    helper_logger.debug("Fetching parameters for this blocks: %s", data)
    if data == "":
        data = "{}"
    return json.loads(data)
