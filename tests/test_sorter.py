from sampletool.sorter import extract_bpm, sort_folder
import tempfile
from pathlib import Path

def test_extract_bpm_standard():
    assert extract_bpm("Bass_Loop_140_Dm") == "140"

def test_extract_bpm_at_end():
    assert extract_bpm("SHADOW_BASS_128") == "128"

def test_extract_bpm_none_when_missing():
    assert extract_bpm("Bass_Loop_Dm") is None

def test_extract_bpm_ignores_non_bpm_numbers():
    # "1401" ne doit pas être détecté comme BPM
    assert extract_bpm("Sample1401") is None

def test_sort_folder_moves_file(tmp_path):
    f = tmp_path / "Bass_140_Dm.wav"
    f.touch()
    stats = sort_folder(tmp_path)
    assert stats["moved"] == 1
    assert (tmp_path / "_140_BPM" / "Bass_140_Dm.wav").exists()

def test_sort_folder_skips_no_bpm(tmp_path):
    f = tmp_path / "BassDm.wav"
    f.touch()
    stats = sort_folder(tmp_path)
    assert stats["skipped"] == 1
    assert f.exists()  # fichier toujours en place

