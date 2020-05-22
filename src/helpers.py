from typing import Any, Union

from geojson import Feature

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


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
