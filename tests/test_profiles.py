from sampletool.profiles import load_profiles, get_profile
import pytest


def test_load_profiles_returns_dict():
    profiles = load_profiles()
    assert isinstance(profiles, dict)
    assert len(profiles) > 0

def test_sp404_profile_exists():
    profile = get_profile("sp404")
    assert profile.target_sample_rate == 48000
    assert profile.target_bit_depth == 16
    assert ".wav" in profile.compatible_formats

def test_lofi_profile_exists():
    profile = get_profile("lo-fi")
    assert profile.target_sample_rate == 22050
    assert profile.target_bit_depth == 8

def test_unknown_profile_raises():
    with pytest.raises(ValueError, match="introuvable"):
        get_profile("inexistant")