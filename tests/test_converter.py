from sampletool.converter import (
    clean_filename, find_audio_files, effective_params,
    needs_conversion, build_output_path, convert_folder
)
from sampletool.profiles import Profile
from pathlib import Path


# Profil de test minimal
TEST_PROFILE = Profile(
    name="test",
    description="Test profile",
    target_sample_rate=48000,
    target_bit_depth=16,
    compatible_formats=[".wav"],
    convert_to=".wav",
    max_filename_length=0,
)


# --- clean_filename ---

def test_clean_filename_removes_spaces_and_dashes():
    assert clean_filename("mon fichier") == "mon_fichier"
    assert clean_filename("Bass_Loop-140") == "Bass_Loop_140"

def test_clean_filename_removes_special_chars():
    assert clean_filename("Bass_Loop-140!") == "Bass_Loop_140"
    assert clean_filename("C#_major") == "C#_major"

def test_clean_filename_keeps_alphanumeric():
    assert clean_filename("Track01") == "Track01"

def test_clean_filename_no_leading_underscore():
    # "! spinz 808" → pas d'underscore en début
    assert clean_filename("! spinz 808") == "spinz_808"

def test_clean_filename_dot_in_name():
    # "evaphin.wav_AVDT" → le point est retiré sans laisser de trace
    assert clean_filename("evaphin.wav_AVDT") == "evaphinwav_AVDT"

def test_clean_filename_multiple_underscores():
    assert clean_filename("Bass - Copy") == "Bass_Copy"

# --- find_audio_files ---

def test_find_audio_files_finds_wav(tmp_path):
    (tmp_path / "test.wav").touch()
    (tmp_path / "image.jpg").touch()
    result = find_audio_files(tmp_path)
    assert len(result) == 1

def test_find_audio_files_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "test.mp3").touch()
    result = find_audio_files(tmp_path)
    assert len(result) == 1


# --- effective_params ---

def test_effective_params_downscale():
    # 96kHz 24bit → 48kHz 16bit : les deux sont réduits
    assert effective_params(96000, 24, 48000, 16) == (48000, 16)

def test_effective_params_no_upsample():
    # 44kHz 16bit → 48kHz 16bit : rate pas monté, depth identique
    assert effective_params(44100, 16, 48000, 16) == (44100, 16)

def test_effective_params_depth_only():
    # 48kHz 24bit → 48kHz 16bit : seule la depth est réduite
    assert effective_params(48000, 24, 48000, 16) == (48000, 16)


# --- needs_conversion ---

def test_needs_conversion_same_params():
    assert needs_conversion(48000, 16, 48000, 16) is False

def test_needs_conversion_higher_depth():
    assert needs_conversion(48000, 24, 48000, 16) is True

def test_needs_conversion_higher_rate():
    assert needs_conversion(96000, 16, 48000, 16) is True

def test_needs_conversion_lower_rate():
    # 44kHz < 48kHz : pas d'upscale, pas de conversion nécessaire
    assert needs_conversion(44100, 16, 48000, 16) is False


# --- build_output_path ---

def test_build_output_path_renames_with_bpm(tmp_path):
    source = tmp_path / "samples"
    source.mkdir()
    output_root = tmp_path / "output"
    f = source / "Bass_140_Am_Loop.wav"
    f.touch()
    out, warns = build_output_path(f, source, output_root, TEST_PROFILE)
    assert out.name == "140_Am_Bass_Loop.wav"

def test_build_output_path_truncates_long_name(tmp_path):
    profile = Profile(
        name="short", description="", target_sample_rate=48000,
        target_bit_depth=16, compatible_formats=[".wav"],
        convert_to=".wav", max_filename_length=10,
    )
    source = tmp_path / "samples"
    source.mkdir()
    f = source / "ThisIsAVeryLongFilename.wav"
    f.touch()
    out, warns = build_output_path(f, source, tmp_path / "out", profile)
    assert len(out.name) <= 10
    assert len(warns) == 1

def test_build_output_path_incompatible_format(tmp_path):
    source = tmp_path / "samples"
    source.mkdir()
    f = source / "loop.ogg"
    f.touch()
    out, _ = build_output_path(f, source, tmp_path / "out", TEST_PROFILE)
    assert out.suffix == ".wav"

def test_convert_folder_output_suffix(tmp_path):
    source = tmp_path / "samples"
    source.mkdir()
    profile = TEST_PROFILE
    stats = convert_folder(source, profile)
    expected_output = tmp_path / "samples_test"  # suffixe = nom du profil
    assert stats["converted"] == 0