from sampletool.sorter import extract_bpm, rename_file_with_bpm, sort_folder
from pathlib import Path


def test_extract_bpm_standard():
    assert extract_bpm("Bass_Loop_140_Dm") == "140"

def test_extract_bpm_at_end():
    assert extract_bpm("SHADOW_BASS_128") == "128"

def test_reject_bpm_below_60():
    assert extract_bpm("Bass_Loop_59_Dm") is None

def test_reject_bpm_above_249():
    assert extract_bpm("Bass_Loop_250_Dm") is None

def test_extract_bpm_none_when_missing():
    assert extract_bpm("Bass_Loop_Dm") is None

def test_extract_bpm_ignores_non_bpm_numbers():
    assert extract_bpm("Sample1401") is None

def test_rename_moves_bpm_to_start(tmp_path):
    f = tmp_path / "trompette_135_loop.wav"
    f.touch()
    rename_file_with_bpm(f)
    assert (tmp_path / "135_trompette_loop.wav").exists()

def test_rename_removes_bpm_from_original_position(tmp_path):
    f = tmp_path / "SHADOW_BASS2_Bass_Loop_Dirt_140_Dm.wav"
    f.touch()
    rename_file_with_bpm(f)
    assert (tmp_path / "140_SHADOW_BASS2_Bass_Loop_Dirt_Dm.wav").exists()

def test_rename_returns_false_when_no_bpm(tmp_path):
    f = tmp_path / "BassDm.wav"
    f.touch()
    assert rename_file_with_bpm(f) is False
    assert f.exists()  # fichier inchangé

def test_sort_folder_stats(tmp_path):
    (tmp_path / "Bass_140_Dm.wav").touch()
    (tmp_path / "BassDm.wav").touch()
    stats = sort_folder(tmp_path)
    assert stats["renamed"] == 1
    assert stats["skipped"] == 1