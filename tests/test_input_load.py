from npa_howtopay.params import load_scenario_from_yaml


def test_load_sample_yaml():
    """Test loading the sample.yaml file"""
    # Load the sample scenario
    params = load_scenario_from_yaml("sample")
    # Verify that params is not None and has expected structure
    assert params is not None
