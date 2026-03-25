from sampletool.converter import clean_filename, find_audio_files
from pathlib import Path
import tempfile


def test_clean_filename_removes_spaces_and_dashes():
    assert clean_filename("mon fichier") == "mon_fichier"
    assert clean_filename("Bass_Loop-140") == "Bass_Loop_140"

def test_clean_filename_removes_special_chars():
    assert clean_filename("Bass_Loop-140!") == "Bass_Loop_140"

def test_clean_filename_keeps_alphanumeric():
    assert clean_filename("Track01") == "Track01"

def test_find_audio_files_finds_wav(tmp_path):
    (tmp_path / "test.wav").touch()
    (tmp_path / "image.jpg").touch()
    result = find_audio_files(tmp_path)
    assert len(result) == 1
    assert result[0].name == "test.wav"

def test_find_audio_files_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "test.mp3").touch()
    result = find_audio_files(tmp_path)
    assert len(result) == 1