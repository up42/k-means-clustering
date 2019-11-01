import os

from geojson import Feature, Point

from context import LOG_FORMAT, get_logger, set_capability, get_capability, load_params


def test_get_logger():
    logger = get_logger("test_logger")
    assert logger.handlers[0].formatter._fmt == LOG_FORMAT, "Incorrect logger or log formatter loaded!" # pylint: disable=protected-access


def test_get_and_set_capability():
    feature = Feature(
        geometry=Point((1, 1)),
        properties={}
    )
    set_capability(feature, "tests-capability", 1)
    assert get_capability(feature, "tests-capability") == 1


def test_load_params():
    os.environ["UP42_TASK_PARAMETERS"] = """
    {
    } 
    """
    assert load_params() == {}

    # Test for nothing not to cause errors
    os.environ["UP42_TASK_PARAMETERS"] = ""
    assert load_params() == {}

    # Test that root level parameters are returned when they are not nested in task name
    os.environ["UP42_TASK_PARAMETERS"] = """
    {
        "test_key": "test_value"
    } 
    """
    assert "test_key" in load_params()
    assert load_params().get("test_key") == "test_value"
